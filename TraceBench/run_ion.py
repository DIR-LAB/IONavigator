import sys
import os
import aiofiles
import json
import asyncio
import time
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.response_synthesizers import ResponseMode
import shutil


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ION"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ion import set_rag_dirs
from ion.Utils import setup_logger, get_root_path, get_path, setup_logger, count_runtime
from ion.Steps.Utils import RAG_DIAGNOSIS_DIR, SUMMARY_FRAGMENT_DIR
from ion.Completions import get_router
from ion.RAG import retrieve_from_index
from ion.Steps import (
    run_rag_diagnosis,
    run_rag_free_diagnosis,
    extract_summary_info,
    intra_module_merge,
    inter_module_merge,
    format_diagnosis_md,
    format_diagnosis_html,
)


tracebench_logger = setup_logger("tracebench_analyze")


def load_rag_index(rag_data_dir, rag_index_dir, embedding_model, reset_index=False):
    tracebench_logger.info(f"Loading RAG index from {rag_index_dir}")
    if reset_index:
        tracebench_logger.info(f"Removing existing RAG index at {rag_index_dir}")
        if os.path.exists(rag_index_dir):
            shutil.rmtree(rag_index_dir)
    if not os.path.exists(rag_index_dir):
        documents = SimpleDirectoryReader(rag_data_dir).load_data()
        tracebench_logger.info(f"Creating new RAG index at {rag_index_dir}")
        index = VectorStoreIndex.from_documents(
            documents, embedding_model=embedding_model
        )
        index.storage_context.persist(persist_dir=rag_index_dir)
    else:
        # NOTE: This is the problematic section, this load_index_from_storage is very slow. Perhaps we can make this so that if the index does not exist, create it, otherwise just utilize the same index
        tracebench_logger.info(f"Loading existing RAG index at {rag_index_dir}")
        storage_context = StorageContext.from_defaults(persist_dir=rag_index_dir)
        index = load_index_from_storage(storage_context)
    return index


async def generate_rag_diagnosis(config, index):
    tracebench_logger.info("Starting RAG diagnosis generation")
    default_model = config["default_model"]
    if "rag_diagnosis" in config["steps"]:
        model = config["steps"]["rag_diagnosis"]["model"]
    else:
        model = default_model
    tracebench_logger.debug(f"Using model: {model}")
    root_path = get_root_path(config)
    summary_dir = get_path([root_path, SUMMARY_FRAGMENT_DIR])
    rag_diagnoses_dir = get_path([root_path, RAG_DIAGNOSIS_DIR])

    rag_enabled = config["RAG"]["enabled"]
    if rag_enabled:
        query_engine = index
        tracebench_logger.info("Initialized RAG query engine")

    async def process_file(file, rag_enabled=True):
        tracebench_logger.info(f"Processing file: {file}")
        async with aiofiles.open(
            os.path.join(summary_dir, file), "r", encoding="utf-8", errors="replace"
        ) as f:
            description = await f.read()

        if rag_enabled:
            tracebench_logger.debug("Retrieving sources from RAG index")
            sources = retrieve_from_index(query_engine, description)
            source_dict = {}
            for idx, source in enumerate(sources):
                _, source_text = source.text.split(":")[0], source.text.split(":")[1]
                file_name = (
                    source.metadata["file_name"]
                    .replace(".md", "")
                    .replace("\uf03a", "/")
                    .replace("\u2215", "/")
                    .replace("\u2044", "/")
                )
                source_dict[f"Source {idx+1}"] = {
                    "file": file_name,
                    "text": source_text,
                }

            tracebench_logger.debug("Running RAG diagnosis")
            diagnosis, updated_source_dict = await run_rag_diagnosis(
                model, default_model, description, source_dict
            )
            diagnosis_dict = {"diagnosis": diagnosis, "sources": updated_source_dict}
        else:
            diagnosis = await run_rag_free_diagnosis(default_model, description)
            diagnosis_dict = {"diagnosis": diagnosis, "sources": {}}

        output_file = os.path.join(rag_diagnoses_dir, file.replace(".txt", ".json"))
        async with aiofiles.open(output_file, "w") as f:
            await f.write(json.dumps(diagnosis_dict, indent=4))
        tracebench_logger.info(f"Saved RAG diagnosis to: {output_file}")

    tasks = []
    for file in os.listdir(summary_dir):
        if rag_enabled:
            tasks.append(process_file(file))
        else:
            tasks.append(process_file(file, rag_enabled=False))
        await asyncio.sleep(0.5)
    tracebench_logger.info(f"Created {len(tasks)} tasks for processing")
    await asyncio.gather(*tasks)
    tracebench_logger.info("All tasks completed")


@count_runtime
async def run_ION(config, models, index, format_md=False):
    get_router(models)

    config = set_rag_dirs(config)

    print("Starting IONPro")
    print("Extracting summary info")
    await extract_summary_info(config)
    print("Generating RAG diagnosis")
    await generate_rag_diagnosis(config, index)
    print("Intra-module merge")
    await intra_module_merge(config)
    print("Inter-module merge")
    final_diagnosis = await inter_module_merge(config)
    print("Formatting diagnosis")
    if format_md:
        final_diagnosis = await format_diagnosis_md(config, final_diagnosis)
    format_diagnosis_html(config, final_diagnosis)
    print("IONPro complete")
    return final_diagnosis
