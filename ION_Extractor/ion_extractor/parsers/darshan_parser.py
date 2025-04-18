import pandas as pd
from .utils import load_darshan_log, get_console, formatted_print
from tqdm import tqdm
import re
import json


def extract_modules(log_data):
    modules = {}
    module = None
    in_module = False
    for line in tqdm(log_data.splitlines()):
        if line.startswith("#<module>"):
            # Extract column names using regex to match all words in <>
            column_names = re.findall(r'<(.*?)>', line)
            in_module = True
        elif in_module:
            if not line.strip():  # Empty line signifies end of module data
                in_module = False
                module = None
            else:
                # Extract module name and ensure correct splitting of fields
                fields = line.split()
                if not module:
                    module = fields[0]  # First field is the module name
                    modules[module] = {'columns': column_names, 'data': []}
                    modules[module]['data'].append(fields)
                else:
                    modules[module]['data'].append(fields)  # Append the entire list of fields
                    # Print for debugging if necessary
                    #print(f"Extracted line: {fields}")
    return modules

def extract_header(log_data):
    header_info = {}
    for line in tqdm(log_data.splitlines()):
        if line.startswith("# nprocs"):
            header_info["nprocs"] = int(line.split(" ")[-1])
        if line.startswith("# run time"):
            header_info["runtime"] = float(line.split(" ")[-1])
        if line.startswith("# start_time:"):
            header_info["start"] = float(line.split(" ")[-1])
        if line.startswith("# end_time:"):
            header_info["end"] = float(line.split(" ")[-1])
    return header_info

def parse_darshan_to_csv(input_file_path, output_dir, save_to_file=True):
    console = get_console()

    # Load the darshan log file
    formatted_print(console, "Loading darshan log file", "green")
    lines = load_darshan_log(input_file_path).splitlines()
    if not lines:
        formatted_print(console, "No data found in the log file", "red")
        return
    else:
        formatted_print(console, "Data loaded successfully", "green")
    
    # Extracting the modules
    formatted_print(console, "Parsing darshan log file", "green")
    try:
        modules = extract_modules(load_darshan_log(input_file_path))
        header = extract_header(load_darshan_log(input_file_path))
    except Exception as e:
        formatted_print(console, f"Error parsing log file: {e}", "red")
        return
    formatted_print(console, "Parsing complete", "green")
    if save_to_file:
        with open(f"{output_dir}/header.json", "w") as f:
            json.dump([header], f, indent=4)
    # Create counter table for each module
    module_dfs = {}
    for module in modules:
        formatted_print(console, f"Found module: {module}", "green")
        columns = modules[module]["columns"]
        rows = modules[module]["data"]
        df = pd.DataFrame(rows, columns=columns)
        index_columns = [column for column in columns if column not in ['counter', 'value']]

        df = df.pivot_table(index=index_columns, columns='counter', values='value', aggfunc='first').reset_index()
        # save the dataframe to a csv file named after the module
        if not save_to_file:
            module_dfs[module] = df
        else:
            formatted_print(console, "Saving data to csv file", "green")
            output_file_path = f"{output_dir}/{module}.csv"
            df.to_csv(output_file_path, index=False)
            formatted_print(console, f"{module} data saved to {output_file_path}", "green")
    
    if not save_to_file:
        return module_dfs, header



    
