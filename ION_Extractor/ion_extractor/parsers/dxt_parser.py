import pandas as pd
from .utils.load import load_dxt_log
from .utils.console import get_console, formatted_print
from tqdm import tqdm

def extract_seq_consec_ops(df):
    # sort by rank and start time
    df.sort_values(by=['rank', 'index'], inplace=True)
    df['shifted_operation'] = df['operation'].shift(1)
    df['shifted_offset'] = df['offset'].shift(1)
    df['shifted_size'] = df['size'].shift(1)
    # if operations are of same type and offset is greater than previous end then they are consecutive
    df['consec'] = df.apply(lambda x: True if x['operation'] == x['shifted_operation'] and x['offset'] >= x['shifted_offset']+x['shifted_size'] else False, axis=1)
    # if offset is equal to previous offset+size then they are sequential
    df['seq'] = df.apply(lambda x: True if x['offset'] == x['shifted_offset']+x['shifted_size'] else False, axis=1)
    # remove shifted columns
    df.drop(columns=['shifted_operation', 'shifted_offset', 'shifted_size'], inplace=True)

    return df

def parse_dxt_txt(txt_output):


    # Lists to store extracted data
    file_ids = []
    file_names = []
    apis = []
    ranks = []
    operations = []
    segments = []
    offsets = []
    sizes = []
    starts = []
    ends = []
    osts = []
    # Variables to hold temporary data
    current_file_id = None
    current_file_name = None
    current_rank = None
    trace_start_time = None
    
    for line in tqdm(txt_output.splitlines()):

        # Extract start time
        if line.startswith("# start_time:"):
            trace_start_time = float(line.split(':')[1].strip())
        
        if line.startswith("# run time:"):
            full_runtime = float(line.split(':')[1].strip())

        # Extract file_id
        if line.startswith("# DXT, file_id:"):
            current_file_id = line.split(':')[1].split(',')[0].strip()
            current_file_name = line.split(':')[2].strip()
            
        # Extract rank
        if line.startswith("# DXT, rank:"):
            current_rank = line.split(':')[1].split(',')[0].strip()
            
        # Extract IO operation details
        if not line.startswith("#") and current_file_id and current_rank:
            parts = line.split()
            # Check if the line has the expected number of fields
            if len(parts) < 8:
                continue
            operations.append(parts[2])
            ranks.append(current_rank)
            file_ids.append(current_file_id)
            file_names.append(current_file_name)
            apis.append(parts[0].split('_')[1])
            segments.append(int(parts[3]))
            if parts[4] == 'N/A':
                offsets.append(0)
            else:
                offsets.append(int(parts[4]))
            if parts[5] == 'N/A':
                sizes.append(0)
            else:
                sizes.append(int(parts[5]))
            starts.append(float(parts[6]) + trace_start_time)
            ends.append(float(parts[7]) + trace_start_time)
            if len(parts) >= 9:
                ost_info = ','.join(parts[9:]).replace(']', '')
                osts.append(ost_info)
            else:
                osts.append('')
                
    # Create DataFrame
    df = pd.DataFrame({
        'file_id': file_ids,
        'file_name': file_names,
        'api': apis,
        'rank': ranks,
        'operation': operations,
        'segment': segments,
        'offset': offsets,
        'size': sizes,
        'start': starts,
        'end': ends,
        'ost': osts
    })
    df = pd.DataFrame.from_dict(df).sort_values(by=['start'])
    df.reset_index(inplace=True)
    # keep only 1000 operations per rank and operation type
    df = df.groupby(['rank', 'operation']).head(10000)
    
    return df, trace_start_time, full_runtime


def parse_dxt_to_csv(log_file, output_dir, save_to_file=True):
    console = get_console()

    formatted_print(console, f"Loading DXT log file: {log_file}", "green")
    try:
        txt_output = load_dxt_log(log_file)
    except Exception as e:
        formatted_print(console, f"Failed to load DXT log file: {log_file}", "red")
        formatted_print(console, f"Error: {e}", "red")
        return None
    if not txt_output:
        formatted_print(console, "Log file data co`uld not be loaded", "red")
        return

    formatted_print(console, f"Parsing DXT log file: {log_file}", "green")
    df, trace_start_time, full_runtime = parse_dxt_txt(txt_output)
    df = extract_seq_consec_ops(df)
    if not df.empty:
        formatted_print(console, "Saving parsed data to CSV", "green")
    else:
        formatted_print(console, "Log failed to parse", "red")
        return
    # save to csv
    if not save_to_file:
        return df, trace_start_time, full_runtime
        
    file_path = f'{output_dir}/DXT.csv'
    df.to_csv(file_path, index=False)
    formatted_print(console, f"Saved parsed data to {file_path}", "green")

    return df, trace_start_time, full_runtime


