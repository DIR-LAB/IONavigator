import argparse
import asyncio
from ION.Utils import get_config
from ION.Completions import get_completion_queue, stop_completion_queue
from ION.Steps import (
    extract_summary_info, 
    generate_rag_diagnosis, 
    intra_module_merge, 
    inter_module_merge, 
    format_diagnosis_html, 
    format_diagnosis_md
)
from ION.Utils import get_metrics, count_runtime
import os
IONPRO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

@count_runtime
async def run_IONPro(config):
    print("Starting IONPro")
    print("Extracting summary info")
    await extract_summary_info(config)
    print("Generating RAG diagnosis")
    await generate_rag_diagnosis(config)
    print("Intra-module merge")
    await intra_module_merge(config)
    print("Inter-module merge")
    final_diagnosis = await inter_module_merge(config)
    return final_diagnosis


async def main():
    parser = argparse.ArgumentParser(description="IONPro: Intelligent Diagnosis of I/O Performance Issues")
    parser.add_argument("--config", type=str, default="../Configs/default_config.json", help="Path to the configuration file")
    parser.add_argument("--trace_path", type=str, help="Optionally set path to the Darshan trace file from command line (overrides config)")
    parser.add_argument("--html", action="store_true", help="Generate HTML output")
    parser.add_argument("--terminal", action="store_true", help="Generate Markdown output")
    args = parser.parse_args()

    # get config
    config = get_config(args.config)
    if args.trace_path:
        config["trace_path"] = args.trace_path
    
    # set rate limit
    get_completion_queue(config["rate_limit"], config["tpm_limit"])
    config["RAG"]["rag_index_dir"] = os.path.join(IONPRO_ROOT, config["RAG"]["rag_index_dir"])
    config["RAG"]["rag_source_data_dir"] = os.path.join(IONPRO_ROOT, config["RAG"]["rag_source_data_dir"])

    datasets_root = os.path.join(IONPRO_ROOT, "TraceBench", "Datasets")
    datasets = ["IO500", "single_issue_bench", "real_app_bench"]
    traces_subdir = "processed_traces"
    for dataset in datasets:
        dataset_path = os.path.join(datasets_root, dataset)
        for trace in os.listdir(os.path.join(dataset_path, traces_subdir)):
            if not ".DS" in trace and not trace in os.listdir(config["analysis_root"]):
                trace_path = os.path.join(dataset_path, traces_subdir, trace)
                config["trace_path"] = trace_path
                final_diagnosis = await run_IONPro(config)
            else:
                if trace in os.listdir(config["analysis_root"]):
                    print(f"Skipping {trace} because it is already analyzed")
                else:
                    print(f"Skipping {trace} because it is a .DS_Store file")
    
    
    if args.html:
        format_diagnosis_html(config, final_diagnosis)
    else:
        print(final_diagnosis["diagnosis"])

    print("final metrics: ", get_metrics())

    stop_completion_queue()

if __name__ == "__main__":
    
    asyncio.run(main())