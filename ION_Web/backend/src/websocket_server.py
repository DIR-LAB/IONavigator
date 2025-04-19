from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from LLM import generate_completion, get_metrics, SYSTEM_PROMPT_REVISED
from chat_agent import TOOLS, TOOL_FUNCTIONS
import json
import traceback
from utils.logging import setup_logger

app = Flask(__name__)
socketio = SocketIO(
    app, 
    cors_allowed_origins=["http://127.0.0.1:3000", "http://localhost:3000", "http://3.138.157.186", "http://ec2-3-138-157-186.us-east-2.compute.amazonaws.com"],
    async_mode='eventlet'
)

CHAT_MODEL = "gpt-4.1-mini"

CORS(app)
metrics_logger = setup_logger('metrics')

def format_chat_prompt(messages, trace_diagnosis):
    messages = messages[1:]
    system_message = {"role": "system", "content": SYSTEM_PROMPT_REVISED.format(trace_diagnosis=trace_diagnosis['content'])}
    return [system_message] + messages

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('send_message')
def handle_message(data):
    print(f"Received message data: {data}")
    try:
        messages = data.get('chat_history')
        user_id = data.get('user_id')
        trace_diagnosis = data.get('trace_diagnosis')
        trace_name = data.get('trace_name')
        
        prompt = format_chat_prompt(messages, trace_diagnosis)
        completion_message = generate_completion(
            CHAT_MODEL,
            prompt,
            tools=TOOLS,
            full_message=True
        )
        
        if completion_message.content:
            socketio.emit('receive_message', {
                'role': 'assistant',
                'content': completion_message.content
            })

        if completion_message.tool_calls:
            # ... rest of your message handling code ...
            pass

        metrics = get_metrics()
        metrics_logger.info(json.dumps(metrics))
        
    except Exception as e:
        print(f"Error in handle_message: {traceback.format_exc()}")
        emit('error', {'message': 'An error occurred while processing your message'})

    finally:
        socketio.emit('response_complete')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)  # Note different port 