import os
import json


def get_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)


def get_root_path(config):
    # This platform agnostic (works on both Mac and Windows) on Mac, and gets the base name of the directory regardless if it uses '/' or '\'
    # application = config["trace_path"].split("/")[-1]
    application = os.path.basename(config["trace_path"])  
    result_path = os.path.join(config['analysis_root'], application)

    return result_path


def get_path(list_of_dirs):
    new_path = os.path.join(*[str(i) for i in list_of_dirs])
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path