import subprocess


def load_dxt_log(log_file):
    if log_file.endswith(".darshan"):
        darshan_txt = subprocess.check_output(["darshan-dxt-parser", "--show-incomplete", log_file])
        darshan_txt = darshan_txt.decode('utf-8')
    else:
        darshan_txt = load_darshan_log(log_file)
    
    return darshan_txt

def load_darshan_log(log_file):
    if log_file.endswith(".darshan"):
        darshan_txt = subprocess.check_output(["darshan-parser", "--show-incomplete", log_file])
        darshan_txt = darshan_txt.decode('utf-8')
    else:
        with open(log_file, 'r') as f:
            darshan_txt = f.read()
    return darshan_txt