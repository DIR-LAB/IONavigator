from parsers import parse_dxt_to_csv
from parsers import parse_darshan_to_csv
from IONPro.Generator.Utils import get_config
import pandas as pd
import argparse
import os
import json

parser = argparse.ArgumentParser(
    description='ION: '
)

parser.add_argument(
    '--config',
    required=False,
    default='../Configs/default_config.json',
    help='Path to the config file'
)

parser.add_argument(
    '--log_file',
    required=False,
    help='Input .darshan file'
)

parser.add_argument(
    '--log_dir',
    required=False,
    help='Input directory containing .darshan files'
)

args = parser.parse_args()

def main():
    config = get_config(args.config)
    log_loc = get_raw_trace_path(config)
    if os.path.isdir(log_loc):
        concat_dir = log_loc
    else:
        concat_dir = None
    
    if not log_loc:
        raise ValueError("No log file or directory provided")
    if os.path.isfile(log_loc) and log_loc.endswith('.darshan'):
        log_file = log_loc
        output_dir = log_loc.split('.')[0]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        parse_darshan_to_csv(log_file, output_dir)


        #parse_dxt_to_csv(log_file, output_dir)
    elif os.path.isdir(log_loc) and args.log_dir:
        log_dir = log_loc
        output_dir = args.output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for log_file in os.listdir(log_dir):
            if log_file.endswith('.darshan'):
                log_file = os.path.join(log_dir, log_file)
                # create a directory in the output directory named after the log file
                out_dir = os.path.join(output_dir, os.path.basename(log_file).split('.')[0])
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                parse_darshan_to_csv(log_file, out_dir)
                try:
                    pass
                    #parse_dxt_to_csv(log_file, out_dir)
                except Exception as e:
                    continue
    elif os.path.isdir(log_loc) and args.concat_dir:
        log_dir = log_loc
        output_dir = args.output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        trace_dfs = {}
        headers = []
        for log_file in os.listdir(log_dir):
            if log_file.endswith('.darshan'):
                log_file = os.path.join(log_dir, log_file)
                # create a directory in the output directory named after the log file
                out_dir = os.path.join(output_dir, os.path.basename(log_file).split('.')[0])
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                
                module_dfs, header_info = parse_darshan_to_csv(log_file, out_dir, save_to_file=False)
                headers.append(header_info)
                for module in module_dfs:
                    if module not in trace_dfs:
                        trace_dfs[module] = module_dfs[module]
                    else:
                        trace_dfs[module] = pd.concat([trace_dfs[module], module_dfs[module]])
                
                try:
                    df, trace_start_time, full_runtime = parse_dxt_to_csv(log_file, out_dir, save_to_file=False)
                    if 'DXT' not in trace_dfs:
                        trace_dfs['DXT'] = df
                    else:
                        trace_dfs['DXT'] = pd.concat([trace_dfs['DXT'], df])
                except Exception as e:
                    continue
        # sort dxt data by start time
        print(trace_dfs)
        trace_dfs['DXT'] = trace_dfs['DXT'].sort_values(by=['start'])
        # save the dataframes to csv files
        for module in trace_dfs:
            file_path = f'{output_dir}/{module}.csv'
            trace_dfs[module].to_csv(file_path, index=False)
        with open(f"{output_dir}/header.json", "w") as f:
            json.dump(headers, f, indent=4)
    else:
        raise ValueError("Invalid log file or directory")
    

if __name__ == '__main__':
    main()

