from ion.Utils import get_root_path, get_path, setup_logger
from ion.Prompts import format_simple_prompt
from ion.Completions import generate_async_completion
from ion.RAG import init_rag_query_engine, retrieve_from_index
from ion.Steps.Utils import RAG_DIAGNOSIS_DIR, SUMMARY_FRAGMENT_DIR
from ion.Prompts.response_formats import RAGDiagnosis
import os
import sys
import json
import asyncio
import aiofiles
import time

rag_diagnosis_logger = setup_logger("rag_diagnosis")


async def run_rag_diagnosis(model, default_model, description, sources):
    rag_diagnosis_logger.info("Running RAG diagnosis generation")
    diagnosis_prompt = format_simple_prompt("rag_diagnosis", {"description": description, "sources": sources})
    response = await generate_async_completion(model=model, messages=diagnosis_prompt, response_format=RAGDiagnosis)
    response_json = RAGDiagnosis.model_validate_json(response)
    diagnosis = response_json.diagnosis
    source_ids = response_json.sources
    source_dict = {}
    source_dict_idx = 1
    for source_id in source_ids:
        source_dict[f"Source {source_dict_idx}"] = sources[f"Source {source_id}"]
        source_dict_idx += 1
    

    return diagnosis, source_dict

async def run_rag_free_diagnosis(model, description):
    rag_diagnosis_logger.info("Running RAG-free diagnosis generation")
    diagnosis_prompt = format_simple_prompt("rag_free_diagnosis", {"description": description})
    response = await generate_async_completion(model=model, messages=diagnosis_prompt)
    return response

async def generate_rag_diagnosis(config):
    rag_diagnosis_logger.info("Starting RAG diagnosis generation")
    default_model = config["default_model"]
    if "rag_diagnosis" in config["steps"]:
        model = config["steps"]["rag_diagnosis"]["model"]
    else:
        model = default_model
    rag_diagnosis_logger.debug(f"Using model: {model}")
    root_path = get_root_path(config)
    summary_dir = get_path([root_path, SUMMARY_FRAGMENT_DIR])
    rag_diagnoses_dir = get_path([root_path, RAG_DIAGNOSIS_DIR])

    rag_enabled = config["RAG"]["enabled"]
    if rag_enabled:
        query_engine = init_rag_query_engine(config["RAG"])
        rag_diagnosis_logger.info("Initialized RAG query engine")

    async def process_file(file, rag_enabled=True):
        rag_diagnosis_logger.info(f"Processing file: {file}")
        async with aiofiles.open(os.path.join(summary_dir, file), "r") as f:
            description = await f.read()

        if rag_enabled:
            rag_diagnosis_logger.debug("Retrieving sources from RAG index")
            sources = retrieve_from_index(query_engine, description)
            source_dict = {}
            for idx, source in enumerate(sources):
                _, source_text = source.text.split(":")[0], source.text.split(":")[1]
                file_name = source.metadata['file_name'].replace('.md', '').replace('\uf03a', '/').replace('\u2215', '/').replace('\u2044', '/')
                source_dict[f"Source {idx+1}"] = {"file": file_name, "text": source_text}

            rag_diagnosis_logger.debug("Running RAG diagnosis")
            diagnosis, updated_source_dict = await run_rag_diagnosis(model, default_model, description, source_dict)
            diagnosis_dict = {"diagnosis": diagnosis, "sources": updated_source_dict}
        else:
            diagnosis = await run_rag_free_diagnosis(default_model, description)
            diagnosis_dict = {"diagnosis": diagnosis, "sources": {}}

        
        output_file = os.path.join(rag_diagnoses_dir, file.replace(".txt", ".json"))
        async with aiofiles.open(output_file, "w") as f:
            await f.write(json.dumps(diagnosis_dict, indent=4))
        rag_diagnosis_logger.info(f"Saved RAG diagnosis to: {output_file}")

    tasks = []
    for file in os.listdir(summary_dir):
        if rag_enabled:
            tasks.append(process_file(file))
        else:
            tasks.append(process_file(file, rag_enabled=False))
        time.sleep(2)
    rag_diagnosis_logger.info(f"Created {len(tasks)} tasks for processing")
    await asyncio.gather(*tasks)
    rag_diagnosis_logger.info("All tasks completed")



if __name__ == "__main__":
    rag_diagnosis_logger.info("Running rag_diagnosis as main")
    default_config = json.load(open("/Users/chris/Documents/Github/IONPro/IONPro/Configs/default_config.json", "r"))
    asyncio.run(generate_rag_diagnosis(default_config))
    rag_diagnosis_logger.info("Completed rag_diagnosis execution")
