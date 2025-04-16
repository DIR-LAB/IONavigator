from parsers import parse_darshan_to_csv
import argparse
import os


def extract_log(log_file_path, output_dir):
    if os.path.isdir(log_file_path):
        for log_file in os.listdir(log_file_path):
            new_log_file_path = os.path.join(log_file_path, log_file)
            log_output_dir = os.path.join(output_dir, log_file.split('.')[0])
            if not os.path.exists(log_output_dir):
                os.makedirs(log_output_dir)
            print(f"Extracting log file: {new_log_file_path} to {log_output_dir}")
            parse_darshan_to_csv(new_log_file_path, log_output_dir)
    else:
        log_output_dir = os.path.join(output_dir, log_file_path.split('/')[-1].split('.')[0])
        if not os.path.exists(log_output_dir):
            os.makedirs(log_output_dir)
        print(f"Extracting log file: {log_file_path} to {log_output_dir}")
        parse_darshan_to_csv(log_file_path, log_output_dir)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=str, help="Path to the log file or directory of log files", required=True)
    parser.add_argument("--output_dir", type=str, help="Path to the output directory", required=True)
    args = parser.parse_args()

    extract_log(args.log, args.output_dir)

