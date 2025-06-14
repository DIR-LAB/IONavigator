import subprocess
import os


def load_dxt_log(log_file):
    if log_file.endswith(".darshan"):
        darshan_txt = subprocess.check_output(["darshan-dxt-parser", "--show-incomplete", log_file])
        darshan_txt = darshan_txt.decode('utf-8')
    else:
        darshan_txt = load_darshan_log(log_file)
    
    return darshan_txt

def load_darshan_log(log_file):
    if log_file.endswith(".darshan"):
        try:
            print(f"Attempting to parse darshan file: {log_file}")
            # Check if file exists and is readable
            if not os.path.exists(log_file):
                raise FileNotFoundError(f"Darshan file not found: {log_file}")
            
            # Check file size
            file_size = os.path.getsize(log_file)
            print(f"Darshan file size: {file_size} bytes")
            
            if file_size == 0:
                raise ValueError(f"Darshan file is empty: {log_file}")
            
            # Try to run darshan-parser with timeout and better error handling
            result = subprocess.run(
                ["darshan-parser", "--show-incomplete", log_file],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode != 0:
                print(f"darshan-parser returned non-zero code: {result.returncode}")
                print(f"stderr: {result.stderr}")
                print(f"stdout length: {len(result.stdout)} characters")
                
                # Check if we got valid output despite the error code
                # darshan-parser often returns -5 (SIGTRAP) for incomplete logs but still produces valid output
                if result.stdout and len(result.stdout.strip()) > 0:
                    print("darshan-parser produced valid output despite error code, proceeding...")
                    darshan_txt = result.stdout
                else:
                    print("darshan-parser failed with no valid output")
                    raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
            else:
                darshan_txt = result.stdout
            
            print(f"Successfully parsed darshan file, output length: {len(darshan_txt)} characters")
            
        except subprocess.TimeoutExpired:
            print(f"darshan-parser timed out after 30 seconds for file: {log_file}")
            raise
        except subprocess.CalledProcessError as e:
            print(f"darshan-parser command failed: {e}")
            print(f"Command: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise
        except Exception as e:
            print(f"Unexpected error parsing darshan file: {e}")
            raise
    else:
        with open(log_file, 'r') as f:
            darshan_txt = f.read()
    return darshan_txt