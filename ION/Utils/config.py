import os
import json


def get_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)


def get_root_path(config):
    application = config["trace_path"].split("/")[-1]
    return os.path.join(config["analysis_root"], application)


def get_path(list_of_dirs):
    new_path = os.path.join(*[str(i) for i in list_of_dirs])
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path