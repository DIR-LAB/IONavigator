from .Steps import (
    extract_summary_info, 
    generate_rag_diagnosis, 
    intra_module_merge, 
    inter_module_merge, 
    format_diagnosis_html
)
from .Utils import count_runtime
import os

ION_ROOT = os.path.dirname(os.path.abspath(__file__))


def set_rag_dirs(config):
    config["RAG"]["rag_index_dir"] = os.path.join(ION_ROOT, config["RAG"]["rag_index_dir"])
    config["RAG"]["rag_source_data_dir"] = os.path.join(ION_ROOT, config["RAG"]["rag_source_data_dir"])
    return config

@count_runtime
async def run_ION(config):
    print("Starting IONPro")
    print("Extracting summary info")
    await extract_summary_info(config)
    print("Generating RAG diagnosis")
    await generate_rag_diagnosis(config)
    print("Intra-module merge")
    await intra_module_merge(config)
    print("Inter-module merge")
    final_diagnosis = await inter_module_merge(config)
    print("Formatting diagnosis")
    format_diagnosis_html(config, final_diagnosis)
    print("IONPro complete")
    return final_diagnosis