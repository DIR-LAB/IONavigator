import re
import pandas as pd
from utils.logging import setup_logger
import json
logger = setup_logger('darshan_utils')



def verify_and_parse_darshan_log(file):
    # Read content directly from FileStorage object instead of using open()
    log_content = file.read().decode('utf-8')  # decode bytes to string
    try:
        modules, header_txt, header_json = parse_darshan_to_csv(log_content)
        # Return strings directly - conversion to bytes should happen at upload time
        return modules, header_txt, header_json
    except Exception as e:
        logger.error(f"Error parsing log file: {e}")
        return None, None, None


skip_lines = [
    "# *WARNING*: The POSIX module contains incomplete data!",
    "#            This happens when a module runs out of",
    "#            memory to store new record data.",
    "# To avoid this error, consult the darshan-runtime",
    "# documentation and consider setting the",
    "# DARSHAN_EXCLUDE_DIRS environment variable to prevent",
    "# Darshan from instrumenting unecessary files.",
]

def extract_modules(log_data):
    modules = {}
    module = None
    in_module = False
    current_description = []
    
    for line in log_data.splitlines():
        if line in skip_lines:
            continue
        # If we find a module header, start collecting description
        if "module data" in line:
            current_description = []
            continue
            
        # If we hit the column definitions, we're done with description
        elif line.startswith("#<module>"):
            column_names = re.findall(r'<(.*?)>', line)
            # if column names have a space, remove it
            column_names = [name.replace(" ", "_") for name in column_names]
            in_module = True
            continue
        # Collect all comment lines as description
        elif line.startswith("#") and not in_module:
            current_description.append(line)
            
        elif in_module:
            if not line.strip():  # Empty line signifies end of module data
                in_module = False
                module = None
            else:
                fields = line.split()
                if not module:
                    module = fields[0]  # First field is the module name
                    modules[module] = {
                        'columns': column_names,
                        'data': [],
                        'description': '\n'.join(current_description)
                    }
                    modules[module]['data'].append(fields)
                else:
                    modules[module]['data'].append(fields)
    
    return modules


def extract_header_txt(log_data):
    # header is every line that is before "# description of columns:"
    # save the lines as text
    header_text = ""
    for line in log_data.splitlines():
        if "# description of columns:" in line:
            break
        else:
            header_text += line + "\n"
    return header_text

def extract_header_json(log_data):
    header_info = {}
    for line in log_data.splitlines():
        if line.startswith("# nprocs"):
            header_info["nprocs"] = int(line.split(" ")[-1])
        if line.startswith("# run time"):
            header_info["runtime"] = float(line.split(" ")[-1])
        if line.startswith("# start_time:"):
            header_info["start"] = float(line.split(" ")[-1])
        if line.startswith("# end_time:"):
            header_info["end"] = float(line.split(" ")[-1])
        if all(key in header_info for key in ["nprocs", "runtime", "start", "end"]):
            break
    # convert to json
    return json.dumps(header_info)

def parse_darshan_to_csv(darshan_content):

    # Load the darshan log file
    logger.info("Loading darshan log file")
    if not darshan_content:
        logger.error("No data found in the log file")
        return
    else:
        logger.info("Data loaded successfully")
    
    # Extracting the modules
    logger.info("Parsing darshan log file")
    try:
        modules = extract_modules(darshan_content)
        header_txt = extract_header_txt(darshan_content)
        header_json = extract_header_json(darshan_content)
    except Exception as e:
        logger.error(f"Error parsing log file: {e}")
        return
    logger.info("Parsing complete")
    # Create counter table for each module
    module_dfs = {}
    for module in modules:
        logger.info(f"Found module: {module}")
        description = modules[module]["description"]
        columns = modules[module]["columns"]
        rows = modules[module]["data"]
        df = pd.DataFrame(rows, columns=columns)
        index_columns = [column for column in columns if column not in ['counter', 'value']]

        df = df.pivot_table(index=index_columns, columns='counter', values='value', aggfunc='first').reset_index()
        # save the dataframe to a csv file named after the module
        module_dfs[module] = {
            "description": description,
            "dataframe": df
        }


    return module_dfs, header_txt, header_json


"""
def process_trace_header(header):
    if type(header) == list and len(header) == 1:
        header = header[0]
    elif type(header) == list and len(header) > 1:
        min_start_time = min([int(item['start']) for item in header])
        max_end_time = max([int(item['end']) for item in header])
        runtime = max_end_time - min_start_time
        nprocs = sum([int(item['nprocs']) for item in header])
        header = {"runtime": runtime, "nprocs": nprocs}

    return header
"""