from ION.Steps.Utils import (get_darshan_modules, 
                                extract_class_methods, 
                                process_trace_header, 
                                summarize_trace_header,
                                DarshanModules,
                                SUMMARY_FRAGMENT_DIR
)
from ION.Completions import generate_async_completion
from ION.Prompts import format_simple_prompt
from ION.Utils import get_root_path, setup_logger

import asyncio
import aiofiles
import os
import traceback
import re
import json


summary_extraction_logger = setup_logger("summary_extraction")

async def generate_summary_document(model, method, return_values):
    summary_extraction_logger.info("Generating summary document")
    prompt = format_simple_prompt("code_interpretation", {"code": method})
    code_interpretation = await generate_async_completion(model, prompt)
    document  = (
        f"In this analysis, the code was described as follows: {code_interpretation}. \n\n"
        f"This is the actual code used to generate this analysis: \n\n{method}. \n\n"
        f"The return value of this analysis is the following: \n\n{return_values}"
    )
    summary_extraction_logger.debug("Summary document generated")
    return document

async def generate_summary_to_rag_document(model, summary_document, module_name, broad_context):
    summary_extraction_logger.info(f"Generating RAG document for {module_name}")
    prompt = format_simple_prompt("summary_to_info", {"module": module_name, "summary": summary_document, "trace_context": broad_context})
    rag_document = await generate_async_completion(model, prompt)
    summary_extraction_logger.debug(f"RAG document generated for {module_name}")
    return rag_document

async def generate_rag_documents(model, module_summaries, broad_context, summary_dir):
    summary_extraction_logger.info("Starting RAG document generation")
    async def process_method(module_name, method, method_return_values, idx):
        summary_extraction_logger.debug(f"Processing method {idx} for {module_name}")
        summary_document = await generate_summary_document(model, method, method_return_values)
        rag_document = await generate_summary_to_rag_document(model, summary_document, module_name, broad_context)
        method_name = re.search(r'def (\w+)', method).group(1)
        rag_document = (f"The {method_name} method in the {module_name} module resulted in the following calculated values: \n\n"
                        f"<json>{method_return_values}</json>\n\n"
                        f"The broader context if the application is as follows: \n\n<json>{broad_context}</json>\n\n"
                        f"The resultant interpretation of the output values given the broader context of the application is as follows: \n\n{rag_document}")
        summary_extraction_logger.info(f"Writing RAG document for {module_name}_{idx}")
        async with aiofiles.open(os.path.join(summary_dir, f"{module_name}_{idx}.txt"), "w", encoding='utf-8') as f:
            await f.write(rag_document)

    tasks = []
    for module_name in module_summaries:
        for idx, method in enumerate(module_summaries[module_name]["methods"]):
            method_return_values = module_summaries[module_name]["summary values"][idx]
            tasks.append(process_method(module_name, method, method_return_values, idx))
    summary_extraction_logger.info(f"Created {len(tasks)} tasks for RAG document generation")
    await asyncio.gather(*tasks)
    summary_extraction_logger.info("RAG document generation completed")

async def extract_summary_info(config):
    summary_extraction_logger.info("Starting summary extraction")
    root_path = get_root_path(config)
    summary_dir = os.path.join(root_path, SUMMARY_FRAGMENT_DIR)
    if not os.path.exists(summary_dir):
        os.makedirs(summary_dir)
        summary_extraction_logger.debug(f"Created summary directory: {summary_dir}")
    
    summary_extraction_logger.info("Getting Darshan modules")
    modules, header = get_darshan_modules(config["trace_path"])
    header = process_trace_header(header)
    module_size_summaries = {}
    module_summaries = {}
    summary_extraction_logger.info("Extracting summary information from each module")

    for module_name in modules:
        if module_name not in list(DarshanModules.keys()):
            continue
        summary_extraction_logger.debug(f"Processing module: {module_name}")
        darshan_module_class = DarshanModules[module_name]
        if module_name == "MPI-IO":
            darshan_module_instance = darshan_module_class(modules[module_name], header["nprocs"])
        else:
            darshan_module_instance = darshan_module_class(modules[module_name])
        module_class_methods = extract_class_methods(darshan_module_class)[1:-1]
        summary_info = darshan_module_instance.summarize()
        if module_name in ["STDIO", "POSIX", "MPI-IO"]:
            module_size_summaries[module_name] = summary_info[0]
        module_summaries[module_name] = {"methods": module_class_methods, "summary values": summary_info}
    
    broad_context = summarize_trace_header(header, module_size_summaries)
    summary_extraction_logger.info("Generating RAG documents")
    if "summary_extraction" in config["steps"]:
        model = config["steps"]["summary_extraction"]["model"]
    else:
        model = config["default_model"]
    summary_extraction_logger.debug(f"Using model: {model}")
    try:
        await generate_rag_documents(model, module_summaries, broad_context, summary_dir)
    except Exception as e:
        summary_extraction_logger.error(f"Error in generate_rag_documents: {e}")
        traceback.print_exc()
        raise e
    summary_extraction_logger.info("Summary extraction completed")

if __name__ == "__main__":
    summary_extraction_logger.info("Running summary_extraction as main")
    default_config = json.load(open("/Users/chris/Documents/Github/IONPro/IONPro/Configs/default_config.json", "r"))
    asyncio.run(extract_summary_info(default_config))
    summary_extraction_logger.info("Summary extraction script completed")






    
    
    


    

