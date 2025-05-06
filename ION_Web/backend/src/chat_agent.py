from interpreter import OpenInterpreter
import json
import os
from ion.Completions import generate_completion
import asyncio
from service_config import s3_client
import shutil
import nest_asyncio

CHAT_MODEL = "gpt-4.1-mini"

ENVIRONMENT_CONTEXT = \
"""
I have processed the Darshan log by splitting each recorded Darshan module into one dataframe and one description string. \
The description string contains information about the data columns in the dataframe as well as some important information about interpreting them while the dataframe contains the actual data for the described columns.\
There is also a dict called `header` which contains the information extracted from the start of the Darshan log which describes the application's total runtime and the number of processes used.\
This is the code I already ran in the environment to setup the data:

```
{setup_code}
```

You must make note of these important points:
1. Do not create any plots or graphs.
2. Only use python code to analyze the data.
3. Only create code where the output is able to be interpreted from the console.
4. Always think of a thorough plan before executing code.
"""


def initialize_interpreter():
    # Apply nest_asyncio to allow nested event loops
    nest_asyncio.apply()
    
    interpreter = OpenInterpreter(sync_computer=True)
    interpreter.llm.model = "anthropic/claude-3-7-sonnet-20250219"
    interpreter.auto_run = True
    interpreter.loop = True
    interpreter.llm.stream = False
    interpreter.llm.max_tokens = 8192
    interpreter.llm.context_window = 200000
    
    return interpreter


def get_darshan_modules(trace_dir: str):
    darshan_modules = []
    for file in os.listdir(trace_dir):
        if file.endswith(".csv"):
            darshan_modules.append(file.replace(".csv", ""))
    return darshan_modules

def prepare_session(darshan_modules: list):
    executed_code = \
"""
import pandas as pd
import numpy as np
import json
import os

with open("header.json", "r") as f:
    header = json.load(f)
"""
    forbidden_chars = ["-", " "]
    for module_name in darshan_modules:
        new_module_name = module_name
        for char in forbidden_chars:
            new_module_name = new_module_name.replace(char, "_")
        executed_code += f"{new_module_name}_data = pd.read_csv('{module_name}.csv')\n"
        executed_code += f"{new_module_name}_description = open('{module_name}_description.txt', 'r').read()\n"
    return executed_code



def format_interpreter_prompt(task_description: str, setup_code: str):
    return ENVIRONMENT_CONTEXT.format(setup_code=setup_code) + "\n\n" + "Here is the task you need to complete:\n " + task_description


def generate_and_execute_code_from_task(task_description: str, trace_name: str, user_id: str):
    current_dir = os.getcwd()
    tmp_dir = os.path.join(current_dir, f"tmp_darshan_analysis/{user_id}/{trace_name}")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    s3_dir = f"{user_id}/{trace_name}/processed_data"
    files = s3_client.list_objects(s3_dir)
    modules = []
    for obj in files:
        if "header.json" in obj['Key']:
            header = s3_client.download_file(obj['Key'])
            with open(os.path.join(tmp_dir, "header.json"), "w") as f:
                f.write(json.dumps(header.decode('utf-8')))
        elif "description.txt" in obj['Key']:
            module_name = obj['Key'].split("/")[-1].replace("_description.txt", "")
            if module_name not in modules:
                modules.append(module_name)
            description = s3_client.download_file(obj['Key'])
            with open(os.path.join(tmp_dir, f"{module_name}_description.txt"), "w") as f:
                f.write(description.decode('utf-8'))
        elif obj['Key'].endswith(".csv"):
            module_name = obj['Key'].split("/")[-1].replace(".csv", "")
            if module_name not in modules:
                modules.append(module_name)
            module_data = s3_client.download_file(obj['Key'])
            with open(os.path.join(tmp_dir, f"{module_name}.csv"), "wb") as f:
                f.write(module_data)

    current_dir = os.getcwd()
    os.chdir(os.path.join(current_dir, tmp_dir))
    try:
        darshan_modules = get_darshan_modules(tmp_dir)
        setup_code = prepare_session(darshan_modules)
        interpreter = initialize_interpreter()
        
        # Create a new event loop for this thread if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the interpreter
        interpreter.computer.run("python", setup_code, display=True)
        interpreter_prompt = format_interpreter_prompt(task_description, setup_code)
        interpreter.chat(interpreter_prompt)
        messages = interpreter.messages
        
        with open("messages.json", "w") as f:
            json.dump(messages, f, indent=4)  
    except Exception as e:
        raise e
    finally:
        os.chdir(current_dir)
        shutil.rmtree(tmp_dir)
    summary = summarize_analysis(messages)
    return summary, messages[-1]['content']


SUMMARY_SYSTEM_PROMPT = \
"""
You are a helpful assistant that summarizes conversations between a user and an AI assistant who is analyzing a Darshan log.
The AI assistant has generated and executed code to which analyzes a Darshan log to complete an analysis task given by the user.
You will be given a list of messages between the user and the AI assistant and the code that was executed by the AI assistant.
You will need to create a summary of this conversation and analysis with the following sections:
- A concise summary of what was done in the analysis
- A summary of the code which was executed by the AI assistant
- A summary of the analysis results
"""

def summarize_analysis(analysis_messages: list):
    prompt = [{'role': 'system', 'content': SUMMARY_SYSTEM_PROMPT},
              {'role': 'user', 'content': "Here is the conversation between the user and the AI assistant:\n" + json.dumps(analysis_messages, indent=4)}]
    response = generate_completion(CHAT_MODEL, prompt)
    return response

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_and_execute_code_from_task",
            "description": "Generate and execute code from a task description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Description of the programming task to be performed"
                    }
                },
                "required": ["task_description"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "generate_and_execute_code_from_task": generate_and_execute_code_from_task
}

