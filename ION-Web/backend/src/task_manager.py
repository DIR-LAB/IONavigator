from enum import Enum
import threading
import queue
import time
from typing import Dict, Optional
import uuid
from service_config import mongodb_client, s3_client
import os
import io
import shutil
import sys
import json
from tree_utils import parse_dir_tree
from IONPro.Generator.Completions import get_completion_queue
from IONPro.Generator.Utils import get_config
from IONPro.Generator.Steps import (
    extract_summary_info, 
    generate_rag_diagnosis, 
    intra_module_merge, 
    inter_module_merge, 
    format_diagnosis_html
)
import asyncio
from datetime import datetime
import traceback
IONPRO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
IONPRO_CONFIG_PATH = os.path.join(IONPRO_ROOT, "IONPro/Configs/default_config.json")
CONFIG = get_config(IONPRO_CONFIG_PATH)

ANALYSIS_DIR = "./tmp_analysis"
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)


class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    def __init__(self, task_id: str, user_id: str, trace_name: str, llm: str):
        self.task_id = task_id
        self.user_id = user_id
        self.trace_name = trace_name
        self.llm = llm
        self.status = TaskStatus.PENDING
        self.progress = 0
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.worker_thread.start()
        self.stop_requested = {}  # Track which tasks should stop
        self.task_loops: Dict[str, asyncio.AbstractEventLoop] = {}  # Track event loops for each task

    def submit_task(self, user_id: str, trace_name: str, llm: str) -> str:
        task_id = str(uuid.uuid4())
        task = Task(task_id, user_id, trace_name, llm)
        self.tasks[task_id] = task
        self.task_queue.put(task)
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        # If task was stopped, return stopped status
        if self.stop_requested.get(task_id):
            return {
                'task_id': task.task_id,
                'status': 'stopped',
                'progress': 0,
                'result': None,
                'error': 'Task stopped by user'
            }
        
        return {
            'task_id': task.task_id,
            'status': task.status.value,
            'progress': task.progress,
            'result': task.result,
            'error': task.error
        }

    def _process_tasks(self):
        while True:
            try:
                task = self.task_queue.get()
                self._run_task(task)
            except Exception as e:
                print(f"Error processing task: {str(e)}")
            finally:
                self.task_queue.task_done()

    def _update_trace_metadata(self, task: Task, status: str):
        try:
            # Get existing metadata
            metadata_path = f"{task.user_id}/{task.trace_name}/metadata.json"
            metadata_content = s3_client.download_file(metadata_path)
            if metadata_content:
                metadata = json.loads(metadata_content)
                # Update status
                metadata['status'] = status
                # Upload updated metadata
                metadata_file = io.BytesIO(json.dumps(metadata).encode())
                s3_client.upload_file(metadata_file, metadata_path)
        except Exception as e:
            print(f"Error updating metadata: {str(e)}")

    def stop_task(self, user_id: str, trace_name: str) -> bool:
        """
        Marks a task for stopping based on user_id and trace_name.
        Returns True if task was found and marked for stopping, False otherwise.
        """
        # Find the task with matching user_id and trace_name
        matching_task = None
        for task in self.tasks.values():
            if task.user_id == user_id and task.trace_name == trace_name:
                matching_task = task
                break

        if matching_task:
            # Mark the task for stopping
            self.stop_requested[matching_task.task_id] = True
            
            # Update metadata to stopped
            self._update_trace_metadata(matching_task, "stopped")
            
            # If task is still running or pending, update its status
            if matching_task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
                matching_task.status = TaskStatus.FAILED
                matching_task.error = "Task stopped by user"
                matching_task.end_time = time.time()
                return True
                
        return False

    def _run_task(self, task: Task):
        analysis_dir = None
        try:
            # Add debug logging to check the model
            print(f"Starting analysis with model: {task.llm['model']}")
            task.status = TaskStatus.RUNNING
            task.start_time = time.time()
            self.stop_requested[task.task_id] = False

            # Update metadata to running
            self._update_trace_metadata(task, "running")

            # Create and set event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.task_loops[task.task_id] = loop  # Store the loop

            # get the trace content from s3
            analysis_dir = os.path.join(ANALYSIS_DIR, task.user_id, task.trace_name)
            if not os.path.exists(analysis_dir):
                os.makedirs(analysis_dir)

            processed_trace_path = f"{task.user_id}/{task.trace_name}/processed_data"
            objects = s3_client.list_objects(processed_trace_path)
            modules = []

            for obj in objects:
                if "header.json" in obj['Key']:
                    header_json = s3_client.download_file(obj['Key'])
                    header_json = json.loads(header_json.decode('utf-8'))
                    with open(os.path.join(analysis_dir, f"header.json"), "w") as f:
                        json.dump(header_json, f)
                if obj['Key'].endswith(".csv"):
                    module_name = obj['Key'].split("/")[-1].split(".")[0]
                    if module_name not in modules:
                        modules.append(module_name)
                    dataframe = s3_client.download_file(obj['Key'])
                    with open(os.path.join(analysis_dir, f"{module_name}.csv"), "wb") as f:
                        f.write(dataframe)
            
            config = CONFIG.copy()
            config["trace_path"] = os.path.join(analysis_dir)
            config["analysis_root"] = os.path.join(analysis_dir, "Output")
            for step in config["steps"]:
                config["steps"][step]["model"] = task.llm['model']
            config["RAG"]["rag_index_dir"] = os.path.join(IONPRO_ROOT, config["RAG"]["rag_index_dir"])
            config["RAG"]["rag_source_data_dir"] = os.path.join(IONPRO_ROOT, config["RAG"]["rag_source_data_dir"])

            get_completion_queue(task.llm["rate_limit"], task.llm["tpm_limit"])

            # Extract summary info
            print("Extracting summary info")
            task.progress = 20
            loop.run_until_complete(extract_summary_info(config))

            # Generate RAG diagnosis
            print("Generating RAG diagnosis")
            task.progress = 30
            loop.run_until_complete(generate_rag_diagnosis(config))

            # Intra-module merge
            print("Intra-module merge")
            task.progress = 40
            loop.run_until_complete(intra_module_merge(config))

            # Inter-module merge
            print("Inter-module merge")
            task.progress = 50
            final_diagnosis = loop.run_until_complete(inter_module_merge(config))

            # Upload results to S3
            new_dir = os.path.join(task.user_id, task.trace_name, "Output")
            output_dir = os.path.join(analysis_dir, "Output")
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    rel_path = root.split("/")[-1]
                    s3_path = os.path.join(new_dir, rel_path, file)
                    with open(os.path.join(root, file), "rb") as f:
                        s3_client.upload_file(f, s3_path)
            
            tree_json = parse_dir_tree(os.path.join(analysis_dir, "Output", task.trace_name))
            tree_json_file = io.BytesIO(json.dumps(tree_json).encode())
            s3_client.upload_file(tree_json_file, os.path.join(new_dir, "tree.json"))

            task.result = final_diagnosis
            task.status = TaskStatus.COMPLETED
            task.end_time = time.time()
            
            # Update metadata to completed
            self._update_trace_metadata(task, "completed")
            task.progress = 100

        except Exception as e:
            print(f"Error running task: {traceback.format_exc()}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            status = "stopped" if self.stop_requested.get(task.task_id) else "failed"
            self._update_trace_metadata(task, status)
            
        finally:
            task.end_time = time.time()
            if task.task_id in self.task_loops:
                loop = self.task_loops[task.task_id]
                try:
                    loop.stop()
                    loop.close()
                except Exception as e:
                    print(f"Error closing event loop: {str(e)}")
                self.task_loops.pop(task.task_id)
                
            if analysis_dir and os.path.exists(analysis_dir):
                try:
                    shutil.rmtree(analysis_dir)
                except Exception as e:
                    print(f"Error cleaning up analysis directory: {str(e)}")
            
            self.stop_requested.pop(task.task_id, None)

    def force_stop_task(self, user_id: str, trace_name: str) -> bool:
        """
        Forcefully stops a task by closing its event loop and cleaning up resources.
        """
        matching_task = None
        for task in self.tasks.values():
            if task.user_id == user_id and task.trace_name == trace_name:
                matching_task = task
                break

        if matching_task:
            # Mark the task for stopping
            self.stop_requested[matching_task.task_id] = True
            
            # Force close the event loop if it exists
            if matching_task.task_id in self.task_loops:
                loop = self.task_loops[matching_task.task_id]
                try:
                    loop.stop()
                    loop.close()
                except Exception as e:
                    print(f"Error force closing event loop: {str(e)}")
                self.task_loops.pop(matching_task.task_id)

            # Update task status
            matching_task.status = TaskStatus.FAILED
            matching_task.error = "Task forcefully stopped by user"
            matching_task.end_time = time.time()
            
            # Update metadata
            self._update_trace_metadata(matching_task, "stopped")
            
            # Clean up analysis directory
            analysis_dir = os.path.join(ANALYSIS_DIR, matching_task.user_id, matching_task.trace_name)
            if os.path.exists(analysis_dir):
                try:
                    shutil.rmtree(analysis_dir)
                except Exception as e:
                    print(f"Error cleaning up analysis directory: {str(e)}")
            
            return True
                
        return False

# Global task manager instance
task_manager = TaskManager() 