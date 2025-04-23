from flask import Flask, request, jsonify
from service_config import mongodb_client, s3_client
from LLM import get_completion_queue, generate_completion, SYSTEM_PROMPT, SYSTEM_PROMPT_REVISED, get_metrics, SUPPORTED_MODELS
from chat_agent import TOOLS, TOOL_FUNCTIONS
from litellm import ChatCompletionMessageToolCall
import uuid
import os
from flask_cors import CORS, cross_origin
import json
import re
import traceback
from utils.logging import setup_logger
from werkzeug.utils import secure_filename
from datetime import datetime
import io
from darshan_utils.log_parser import verify_and_parse_darshan_log
from obj_types import (
    User, ChatMessage, ChatHistory, TraceMetadata, 
    TraceDiagnosis, APIResponse, UploadTraceResponse, UserResponse
)
from io import StringIO, BytesIO
import sys
sys.path.append('../../..')
from task_manager import task_manager
from ION.Steps import json_to_html, md_to_html
from ion_extractor.parsers.utils import load_darshan_log

ANALYSIS_DIR = "./tmp_analysis"
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:3000", "http://localhost:3000", "http://3.138.157.186", "http://ec2-3-138-157-186.us-east-2.compute.amazonaws.com"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/public/*": {"origins": "*"}
})
open_cors = CORS()

CHAT_MODEL = "gpt-4o"




metrics_logger = setup_logger('metrics')
backend_logger = setup_logger('backend')

@app.route('/api/user', methods=['POST'])
def add_user():
    email = request.json.get('email')
    if not email:
        return APIResponse(
            error='Email is required',
            status_code=400
        ).model_dump(), 400
    
    user_id, message, status_code = mongodb_client.add_user(email)
    return UserResponse(
        user_id=user_id,
        message=message
    ).model_dump(), status_code



@app.route('/api/user_traces', methods=['POST'])
def fetch_user_traces():
    user_id = request.json.get('user_id')
    user = mongodb_client.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        print(f"Listing objects for user_id: {user_id}")
        response = s3_client.s3_client.list_objects_v2(
            Bucket=s3_client.bucket_name,
            Prefix=f"{user_id}/",
            Delimiter='/'
        )
        
        traces = []
        for prefix in response.get('CommonPrefixes', []):
            trace_name = prefix.get('Prefix').split('/')[1]
            metadata_path = f"{user_id}/{trace_name}/metadata.json"
            print(f"Attempting to fetch metadata from: {metadata_path}")
            
            try:
                metadata_content = s3_client.download_file(metadata_path)
                if metadata_content:
                    metadata = json.loads(metadata_content)
                    traces.append({
                        'trace_name': metadata['trace_name'],
                        'trace_description': metadata['trace_description'],
                        'upload_date': metadata['upload_date'],
                        'status': metadata.get('status', 'not_started'),
                        'model': metadata.get('model', 'gpt-4o')  # Include model from metadata
                    })
                    print(f"Successfully loaded metadata for trace: {trace_name}")
                else:
                    print(f"No metadata content found for trace: {trace_name}")
            except Exception as e:
                print(f"Error fetching metadata for trace {trace_name}: {str(e)}")
                continue
        
        if not traces:
            print("No traces found")
            return jsonify([]), 200
            
        traces = sorted(traces, key=lambda x: x['upload_date'], reverse=True)
        return jsonify(traces), 200
        
    except Exception as e:
        print(f"Error fetching traces: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch traces'}), 500

@app.route('/api/trace_examples/<trace_name>/final_diagnosis', methods=['POST'])
def fetch_trace_example(trace_name):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        # Get the diagnosis from S3
        diagnosis_path = f"{user_id}/{trace_name}/Output/final_diagnosis/final_diagnosis.json"
        print(f"Attempting to fetch diagnosis from S3: {diagnosis_path}")
        
        diagnosis_content = s3_client.download_file(diagnosis_path)
        if not diagnosis_content:
            return jsonify({'error': 'Diagnosis not found'}), 404
            
        trace_diagnosis = json.loads(diagnosis_content)
        print(f"trace_diagnosis: {trace_diagnosis}")
        citations = process_diagnosis_sources(trace_diagnosis)
        new_id = str(uuid.uuid4())
        
        return jsonify({
            'trace_diagnosis': {
                'content': trace_diagnosis['diagnosis'], 
                'sources': citations
            }, 
            'id': new_id
        }), 200
        
    except Exception as e:
        print(f"Error fetching trace example: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch trace example'}), 500

def process_diagnosis_sources(final_diagnosis):
    sources = final_diagnosis['sources']
    new_sources = []
    idx = 1
    for source in sources:
        new_sources.append({
            'id': idx,
            'file': sources[source]['file'],
            'text': sources[source]['text']
        })
        idx += 1
    print(f"new_sources: {new_sources}")
    return new_sources


def format_chat_prompt(messages, trace_diagnosis):
    #remove diagnosis content from messages
    messages = messages[1:]
    system_message = {"role": "system", "content": SYSTEM_PROMPT_REVISED.format(trace_diagnosis=trace_diagnosis['content'])}
    messages = [system_message] + messages
    return messages

@app.route('/api/run_analysis', methods=['POST'])
@cross_origin(origin="*")
def run_analysis():
    user_id = request.json.get('user_id')
    trace_name = request.json.get('trace_name')
    llm = request.json.get('llm')
    
    # update the model in the metadata
    metadata_path = f"{user_id}/{trace_name}/metadata.json"
    metadata_content = s3_client.download_file(metadata_path)
    if not metadata_content:
        return jsonify({'error': 'Metadata not found'}), 404
        
    # Parse the JSON from bytes
    metadata = json.loads(metadata_content)
    metadata['model'] = llm
    
    # Convert back to JSON string and then to bytes for upload
    metadata_json = json.dumps(metadata)
    metadata_file = io.BytesIO(metadata_json.encode())
    if not s3_client.upload_file(metadata_file, metadata_path):
        return jsonify({'error': 'Failed to update metadata'}), 500
    
    if not user_id or not trace_name:
        return jsonify({'error': 'User ID and trace name are required'}), 400

    # Submit the analysis task to the task manager
    if llm not in SUPPORTED_MODELS:
        return jsonify({'error': 'Invalid model'}), 400
    else:
        task_id = task_manager.submit_task(user_id, trace_name, SUPPORTED_MODELS[llm])
    
    return jsonify({
        'task_id': task_id,
        'message': 'Analysis task submitted successfully'
    }), 202

@app.route('/api/analysis_status/<task_id>', methods=['GET'])
def get_analysis_status(task_id):
    status = task_manager.get_task_status(task_id)
    if not status:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(status), 200

@app.route('/api/trace_examples/<trace_name>/original_trace', methods=['POST'])
@cross_origin(origin="*")
def fetch_original_trace(trace_name):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
        
    original_trace_path = f"{user_id}/{trace_name}/trace_data/original_trace.txt"
    
    try:
        print(f"Attempting to fetch original trace from S3: {original_trace_path}")
        
        # Initialize variables for chunked reading
        chunk_size = 8192  # 8KB chunks
        start_byte = 0
        lines = []
        line_buffer = ""
        
        while len(lines) < 2000:
            chunk = s3_client.download_file_chunk(original_trace_path, start_byte, chunk_size)
            if not chunk:  # End of file or error
                break
                
            # No more data to read
            if len(chunk) == 0:
                break
                
            # Decode chunk and add to buffer
            chunk_str = chunk.decode('utf-8')
            line_buffer += chunk_str
            
            # Split buffer into lines
            new_lines = line_buffer.splitlines()
            
            # If the chunk doesn't end with a newline, keep the last partial line in the buffer
            if not chunk_str.endswith('\n'):
                line_buffer = new_lines[-1]
                new_lines = new_lines[:-1]
            else:
                line_buffer = ""
            
            lines.extend(new_lines)
            start_byte += len(chunk)
            
            # If we have more than 2000 lines, truncate
            if len(lines) >= 2000:
                lines = lines[:2000]
                break
        
        if not lines:
            return jsonify({'error': 'Original trace is empty'}), 404
            
        original_trace = '\n'.join(lines)
        if start_byte > chunk_size:  # If we had to truncate
            original_trace += "\n...Truncated at 2000 lines..."
            
        return jsonify({'original_trace': original_trace}), 200
        
    except Exception as e:
        print(f"Error fetching original trace: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch original trace'}), 500

@app.route('/api/trace_examples/<trace_name>/html_diagnosis', methods=['GET'])
def fetch_diagnosis_html(trace_name):
    # Path to the diagnosis HTML file
    user_id = request.json.get('user_id')
    diagnosis_file_path = f"{user_id}/{trace_name}/Output/trace_data/final_diagnosis.html"
    
    try:
        with open(diagnosis_file_path, 'r') as f:
            diagnosis_html = f.read()
        return diagnosis_html, 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return jsonify({'error': 'Diagnosis file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/trace_examples/<trace_name>/sample_questions', methods=['POST'])
def fetch_sample_questions(trace_name):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
        
    try:
        # Get sample questions from S3
        questions_path = f"sample_questions.json"
        print(f"Attempting to fetch sample questions from S3: {questions_path}")
        
        questions_content = s3_client.download_file(questions_path)
        if not questions_content:
            return jsonify({'error': 'Sample questions not found'}), 404
            
        sample_questions = json.loads(questions_content)
        return jsonify(sample_questions), 200
        
    except Exception as e:
        print(f"Error fetching sample questions: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch sample questions'}), 500

@app.route('/api/update_history', methods=['POST'])
def update_history():
    chat_history = request.json.get('chat_history')
    history_id = chat_history.pop('id')
    user_id = request.json.get('user_id')
    
    success, message, status_code = mongodb_client.update_chat_history(
        user_id, 
        history_id, 
        chat_history
    )
    
    if success:
        return jsonify({'message': message}), status_code
    return jsonify({'error': message}), status_code

ALLOWED_EXTENSIONS = {'txt', 'darshan'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload_trace', methods=['POST'])
@cross_origin(origin="*")
def upload_trace():
    if 'file' not in request.files:
        return APIResponse(
            error='No file part',
            status_code=400
        ).model_dump(), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    
    if file and allowed_file(file.filename):
        if file.filename.endswith('.darshan'):
            # Read the file content first and store it
            
            # Create analysis directory if it doesn't exist
            os.makedirs(ANALYSIS_DIR, exist_ok=True)
            
            # Save the file temporarily to process with darshan-parser
            temp_path = os.path.join(ANALYSIS_DIR, secure_filename(file.filename))
            print(f"temp_path: {temp_path}")
            try:
                file.save(temp_path)
                file_content = load_darshan_log(temp_path)
                file_content = file_content.encode()

            except (IOError, OSError) as e:
                return jsonify({'error': f'Failed to save temporary file: {str(e)}'}), 500
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        print(f"Warning: Failed to remove temporary file {temp_path}")
                        
            # Create BytesIO object with the original content for S3 upload
            file_obj = io.BytesIO(file_content)
        else:
            # For non-darshan files
            file_content = file.read()
            file_obj = io.BytesIO(file_content)
            
        filename = secure_filename(file.filename)
        trace_name = os.path.splitext(filename)[0]
        metadata = TraceMetadata(
            trace_name=trace_name,
            trace_description='User uploaded trace',
            upload_date=datetime.now(),
            status='not_started',
            model='gpt-4o'  # Set default model
        )
        
        # Upload trace file to S3
        trace_path = f"{user_id}/{trace_name}/trace_data/original_trace.txt"
        metadata_path = f"{user_id}/{trace_name}/metadata.json"

        # check if the trace file already exists
        if s3_client.check_if_exists(trace_path):
            return jsonify({'error': 'Trace file already exists'}), 400

        # Create a new BytesIO object with the same content for parsing
        parse_file_obj = io.BytesIO(file_content)
        parse_file_obj.name = filename  # Add name attribute to mimic FileStorage object
        
        # verify and parse the trace file
        modules, header_txt, header_json = verify_and_parse_darshan_log(parse_file_obj)
        if modules is None or header_txt is None or header_json is None:
            return jsonify({'error': 'Failed to parse trace file'}), 500
        
        modules_path = f"{user_id}/{trace_name}/processed_data"

        # upload header to s3
        header_path = f"{modules_path}/header.txt"
        header_txt_obj = io.BytesIO(header_txt.encode())
        if not s3_client.upload_file(header_txt_obj, header_path):
            return jsonify({'error': 'Failed to upload header text'}), 500
        
        # upload header json to s3
        header_json_path = f"{modules_path}/header.json"
        header_json_obj = io.BytesIO(header_json.encode())
        if not s3_client.upload_file(header_json_obj, header_json_path):
            return jsonify({'error': 'Failed to upload header json'}), 500
        
        for module in modules:
            description = modules[module]["description"]
            dataframe = modules[module]["dataframe"]
            # upload description to s3
            description_path = f"{modules_path}/{module}_description.txt"
            description_obj = io.BytesIO(description.encode())
            if not s3_client.upload_file(description_obj, description_path):
                return jsonify({'error': 'Failed to upload description to S3'}), 500
            # upload dataframe to s3
            dataframe_path = f"{modules_path}/{module}.csv"
            dataframe_obj = io.BytesIO(dataframe.to_csv().encode())
            if not s3_client.upload_file(dataframe_obj, dataframe_path):
                return jsonify({'error': 'Failed to upload dataframe to S3'}), 500
        
        # Upload original trace file using the stored content
        if not s3_client.upload_file(file_obj, trace_path):
            return jsonify({'error': 'Failed to upload trace file to S3'}), 500
        
        # Convert to dict and handle datetime serialization
        metadata_dict = metadata.model_dump()
        metadata_dict['upload_date'] = metadata_dict['upload_date'].strftime("%Y-%m-%d %H:%M:%S")
        
        # Upload metadata
        metadata_json = json.dumps(metadata_dict)
        metadata_file = io.BytesIO(metadata_json.encode())
        if not s3_client.upload_file(metadata_file, metadata_path):
            return jsonify({'error': 'Failed to upload metadata to S3'}), 500
        
        return UploadTraceResponse(
            message='File uploaded successfully',
            trace_name=trace_name
        ).model_dump(), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/delete_trace', methods=['POST'])
@cross_origin(origin="*")
def delete_trace():
    user_id = request.json.get('user_id')
    trace_name = request.json.get('trace_name')
    
    if not user_id or not trace_name:
        return jsonify({'error': 'User ID and trace name are required'}), 400
        
    try:
        # Delete all objects under the trace prefix
        prefix = f"{user_id}/{trace_name}/"
        response = s3_client.s3_client.list_objects_v2(
            Bucket=s3_client.bucket_name,
            Prefix=prefix
        )
        
        if 'Contents' in response:
            objects = [{'Key': obj['Key']} for obj in response['Contents']]
            s3_client.s3_client.delete_objects(
                Bucket=s3_client.bucket_name,
                Delete={'Objects': objects}
            )
            
        return jsonify({'message': 'Trace deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting trace: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to delete trace'}), 500

@app.route('/api/trace_examples/<trace_name>/diagnosis_tree', methods=['POST'])
def fetch_diagnosis_tree(trace_name):
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        # Get the tree.json from S3
        tree_path = f"{user_id}/{trace_name}/Output/tree.json"
        print(f"Attempting to fetch diagnosis tree from S3: {tree_path}")
        
        tree_content = s3_client.download_file(tree_path)
        if not tree_content:
            return jsonify({'error': 'Diagnosis tree not found'}), 404
            
        tree_data = json.loads(tree_content)
        return jsonify(tree_data), 200
        
    except Exception as e:
        print(f"Error fetching diagnosis tree: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch diagnosis tree'}), 500

@app.route('/api/render_content', methods=['POST'])
def render_content():
    try:
        content = request.json.get('content')
        if type(content) == dict:
            html_content = json_to_html(content)
        else:
            html_content = md_to_html(content)
        return html_content, 200
    except Exception as e:
        print(f"Error rendering content: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to render content'}), 500

@app.route('/api/rename_trace', methods=['POST'])
def rename_trace():
    user_id = request.json.get('user_id')
    old_name = request.json.get('old_name')
    new_name = request.json.get('new_name')
    
    if not all([user_id, old_name, new_name]):
        return jsonify({'error': 'User ID, old name, and new name are required'}), 400
        
    try:
        # Check if new name already exists
        new_prefix = f"{user_id}/{new_name}/"
        response = s3_client.s3_client.list_objects_v2(
            Bucket=s3_client.bucket_name,
            Prefix=new_prefix,
            MaxKeys=1
        )
        if response.get('Contents'):
            return jsonify({'error': 'A trace with this name already exists'}), 409

        # List all objects under the old prefix
        old_prefix = f"{user_id}/{old_name}/"
        response = s3_client.s3_client.list_objects_v2(
            Bucket=s3_client.bucket_name,
            Prefix=old_prefix
        )
        
        if not response.get('Contents'):
            return jsonify({'error': 'Original trace not found'}), 404
            
        # Copy each object to new location and delete old one
        for obj in response['Contents']:
            old_key = obj['Key']
            new_key = old_key.replace(old_prefix, new_prefix)
            
            # Copy object to new location
            s3_client.s3_client.copy_object(
                Bucket=s3_client.bucket_name,
                CopySource={'Bucket': s3_client.bucket_name, 'Key': old_key},
                Key=new_key
            )
            
            # Delete old object
            s3_client.s3_client.delete_object(
                Bucket=s3_client.bucket_name,
                Key=old_key
            )
            
        # Update metadata file with new name
        metadata_path = f"{user_id}/{new_name}/metadata.json"
        metadata_content = s3_client.download_file(metadata_path)
        if metadata_content:
            metadata = json.loads(metadata_content)
            metadata['trace_name'] = new_name
            metadata_json = json.dumps(metadata)
            metadata_file = io.BytesIO(metadata_json.encode())
            s3_client.upload_file(metadata_file, metadata_path)
            
        return jsonify({'message': 'Trace renamed successfully'}), 200
        
    except Exception as e:
        print(f"Error renaming trace: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to rename trace'}), 500

@app.route('/api/stop_analysis', methods=['POST'])
@cross_origin(origin="*")
def stop_analysis():
    user_id = request.json.get('user_id')
    trace_name = request.json.get('trace_name')
    
    if not user_id or not trace_name:
        return jsonify({'error': 'User ID and trace name are required'}), 400

    try:
        # Try graceful stop first, then force stop if needed
        if not task_manager.stop_task(user_id, trace_name):
            task_manager.force_stop_task(user_id, trace_name)
        
        return jsonify({
            'message': 'Analysis stopped successfully'
        }), 200
        
    except Exception as e:
        print(f"Error stopping analysis: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to stop analysis'}), 500

@app.route('/api/update_trace_model', methods=['POST'])
def update_trace_model():
    user_id = request.json.get('user_id')
    trace_name = request.json.get('trace_name')
    model = request.json.get('model')
    
    if not all([user_id, trace_name, model]):
        return jsonify({'error': 'User ID, trace name, and model are required'}), 400

    try:
        # Get existing metadata
        metadata_path = f"{user_id}/{trace_name}/metadata.json"
        metadata_content = s3_client.download_file(metadata_path)
        if not metadata_content:
            return jsonify({'error': 'Trace metadata not found'}), 404
            
        metadata = json.loads(metadata_content)
        
        # Update model in metadata
        metadata['model'] = model
        
        # Upload updated metadata
        metadata_file = io.BytesIO(json.dumps(metadata).encode())
        if not s3_client.upload_file(metadata_file, metadata_path):
            return jsonify({'error': 'Failed to update metadata'}), 500
        
        return jsonify({'message': 'Model updated successfully'}), 200
        
    except Exception as e:
        print(f"Error updating trace model: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to update trace model'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)