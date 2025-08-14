import os
import json


def get_label_codes(root_dir):
    # load the labels json file
    labels_file = os.path.join(root_dir, "Dataset_Labels.json")
    with open(labels_file, "r") as f:
        labels = json.load(f)
    return labels