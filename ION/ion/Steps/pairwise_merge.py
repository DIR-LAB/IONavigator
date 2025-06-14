import os
import json
import asyncio
import aiofiles
import uuid
from ion.Utils import get_root_path, get_path, setup_logger
from ion.Prompts import format_merge_prompt, RAGDiagnosis
from ion.Completions import generate_async_completion
from ion.Steps.Utils import (
    RAG_DIAGNOSIS_DIR,
    INTRA_MODULE_MERGE_DIR,
    INTER_MODULE_MERGE_DIR,
    FINAL_MODULE_MERGE_DIR,
    FINAL_DIAGNOSIS_DIR,
    FINAL_DIAGNOSIS_NAME
)

intra_merge_logger = setup_logger("intra_module_merge")
inter_merge_logger = setup_logger("inter_module_merge")

##########################################################################
# ########## INTRA-MODULE MERGE ##########
##########################################################################


async def merge_intra_module_diagnoses(model, default_model, module_name, diagnosis1, diagnosis2, file_name, merge_dir, final=False, rag_enabled=True):
    intra_merge_logger.info(
        f"Merging intra-module diagnoses for module: {module_name}")
    unique_id = str(uuid.uuid4())
    inject_string = ""
    if not rag_enabled:
        inject_string = "rag_free_"
    if final:
        merge_prompt, combined_source_list = format_merge_prompt(
            f"final_{inject_string}intra_module_merge", diagnosis1, diagnosis2, {"module": module_name})
    else:
        merge_prompt, combined_source_list = format_merge_prompt(
            f"{inject_string}intra_module_merge", diagnosis1, diagnosis2, {"module": module_name})

    intra_merge_logger.debug(f"Generated merge prompt with ID: {unique_id}")
    merged_diagnosis = await generate_async_completion(model, merge_prompt, response_format=MergedDiagnosis)
    merged_diagnosis_json = MergedDiagnosis.model_validate_json(
        merged_diagnosis)
    merged_diagnosis = merged_diagnosis_json.diagnosis
    sources_ids = merged_diagnosis_json.sources
    updated_source_dict = {}

    for source_id in sources_ids:
        updated_source_dict[f"Source {source_id}"] = combined_source_list[f"Source {source_id}"]

    merged_diagnosis_dict = {
        "diagnosis": merged_diagnosis, "sources": updated_source_dict}

    output_file = os.path.join(merge_dir, str(file_name)+".json")
    async with aiofiles.open(output_file, "w") as f:
        await f.write(json.dumps(merged_diagnosis_dict, indent=4))
    intra_merge_logger.info(f"Saved merged diagnosis to: {output_file}")

    return merged_diagnosis_dict


async def run_async_intra_module_merge(module_rag_diagnoses, module_name, config):
    intra_merge_logger.info(
        f"Starting intra-module merge for module: {module_name}")
    root_path = get_root_path(config)
    intra_merge_dir = get_path([root_path, INTRA_MODULE_MERGE_DIR])
    default_model = config["default_model"]
    if "intra_module_merge" in config["steps"]:
        model = config["steps"]["intra_module_merge"]["model"]
    else:
        model = default_model

    rag_enabled = config["RAG"]["enabled"]

    # split list into pairs and merge in parallel
    # if odd number of elements, last element is a singleton and will be merged in next step
    merge_step = 1
    current_merge_dir = get_path([intra_merge_dir, module_name, merge_step])
    remaining_fragments = len(module_rag_diagnoses)
    while remaining_fragments > 2:
        intra_merge_logger.debug(
            f"Merge step {merge_step} for module {module_name}, remaining fragments: {remaining_fragments}")
        tasks = []
        for i in range(0, len(module_rag_diagnoses)-1, 2):
            intra_merge_logger.debug(f"Merging fragments {i} and {i+1}")
            fragment1 = module_rag_diagnoses[i]
            fragment2 = module_rag_diagnoses[i+1]
            intra_merge_logger.debug(f"Fragment 1: {fragment1}")
            intra_merge_logger.debug(f"Fragment 2: {fragment2}")
            if rag_enabled:
                tasks.append(merge_intra_module_diagnoses(
                    model, default_model, module_name, fragment1, fragment2, i, current_merge_dir))
            else:
                tasks.append(merge_intra_module_diagnoses(model, default_model, module_name,
                             fragment1, fragment2, i, current_merge_dir, rag_enabled=False))

        # if odd number of elements, last element is copied to next step
        if len(module_rag_diagnoses) % 2 == 1:
            singleton = module_rag_diagnoses[-1]
            with open(os.path.join(current_merge_dir, f"{len(module_rag_diagnoses)-1}.json"), "w") as f:
                json.dump(module_rag_diagnoses[-1], f, indent=4)
            intra_merge_logger.debug(
                f"Saved singleton fragment to: {os.path.join(current_merge_dir, f'{len(module_rag_diagnoses)-1}.json')}")
        else:
            singleton = None

        module_rag_diagnoses = await asyncio.gather(*tasks)
        if singleton is not None:
            module_rag_diagnoses.append(singleton)
            intra_merge_logger.debug(
                f"Added singleton fragment to module_rag_diagnoses: {singleton}")
        remaining_fragments = len(module_rag_diagnoses)
        merge_step += 1
        intra_merge_logger.debug(
            f"Completed merge step {merge_step-1} for module {module_name}, new remaining fragments: {remaining_fragments}")
        if remaining_fragments > 2:
            current_merge_dir = get_path(
                [intra_merge_dir, module_name, merge_step])

    # final merge step
    final_merge_dir = get_path([root_path, FINAL_MODULE_MERGE_DIR])
    intra_merge_logger.info(
        f"Performing final intra-module merge for module: {module_name}")
    await merge_intra_module_diagnoses(model, default_model, module_name, module_rag_diagnoses[0], module_rag_diagnoses[1], module_name, final_merge_dir, final=True)


async def intra_module_merge(config):
    intra_merge_logger.info("Starting intra-module merge process")
    root_path = get_root_path(config)
    rag_diagnoses_dir = get_path([root_path, RAG_DIAGNOSIS_DIR])

    rag_diagnoses = {}
    for file in os.listdir(rag_diagnoses_dir):
        if ".json" not in file:
            continue
        module_name = file.split("_")[0]
        if module_name not in rag_diagnoses:
            rag_diagnoses[module_name] = []
        with open(os.path.join(rag_diagnoses_dir, file), "r") as f:
            rag_diagnoses[module_name].append(json.load(f))

    modules = list(rag_diagnoses.keys())
    intra_merge_logger.info(f"Found {len(modules)} modules to merge")
    tasks = [run_async_intra_module_merge(
        rag_diagnoses[module], module, config) for module in modules]
    await asyncio.gather(*tasks)
    intra_merge_logger.info("Completed intra-module merge process")

##########################################################################
# ########## INTER-MODULE MERGE ##########
##########################################################################


def combine_sources_content(source_dict):
    # combine the content of all sources which have the same file name
    combined_sources = {}
    for _, source_content in source_dict.items():
        file_name = source_content["file"]
        if file_name not in combined_sources:
            combined_sources[file_name] = []
        if source_content["text"] not in combined_sources[file_name]:
            combined_sources[file_name].append(source_content["text"])
    idx = 1
    new_source_dict = {}
    for file_name, source_content in combined_sources.items():
        new_source_dict[f"Source {idx}"] = {
            "file": file_name, "text": "\n".join(source_content)}
        idx += 1
    return new_source_dict


async def merge_inter_module_diagnoses(model, default_model, module_names, module1_data, module2_data, file_name, merge_dir, final=False, rag_enabled=True):
    inter_merge_logger.info(
        f"Merging inter-module diagnoses for modules: {', '.join(module_names)}")
    unique_id = str(uuid.uuid4())
    inject_string = ""
    if not rag_enabled:
        inject_string = "rag_free_"
    if final:
        if 'o1' in model:
            merge_prompt, combined_sources = format_merge_prompt(
                f"final_{inject_string}inter_module_merge_o1", module1_data, module2_data, {"all_modules": module_names})
        else:
            merge_prompt, combined_sources = format_merge_prompt(
                f"final_{inject_string}inter_module_merge", module1_data, module2_data, {"all_modules": module_names})
    else:
        if 'o1' in model:
            merge_prompt, combined_sources = format_merge_prompt(
                f"{inject_string}inter_module_merge_o1", module1_data, module2_data, {"all_modules": module_names})
        else:
            merge_prompt, combined_sources = format_merge_prompt(
                f"{inject_string}inter_module_merge", module1_data, module2_data, {"all_modules": module_names})

    inter_merge_logger.debug(f"Generated merge prompt with ID: {unique_id}")
    merged_diagnosis = await generate_async_completion(model, merge_prompt, response_format=MergedDiagnosis)
    merged_diagnosis_json = MergedDiagnosis.model_validate_json(
        merged_diagnosis)
    merged_diagnosis = merged_diagnosis_json.diagnosis
    sources_ids = merged_diagnosis_json.sources
    updated_source_dict = {}
    for source_id in sources_ids:
        updated_source_dict[f"Source {source_id}"] = combined_sources[f"Source {source_id}"]

    inter_merge_logger.debug(f"Received merged diagnosis for ID: {unique_id}")
    if rag_enabled:
        if final:
            merged_diagnosis_dict = {"diagnosis": merged_diagnosis,
                                     "sources": combine_sources_content(updated_source_dict)}
        else:
            merged_diagnosis_dict = {
                "diagnosis": merged_diagnosis, "sources": updated_source_dict}
    else:
        merged_diagnosis_dict = {"diagnosis": merged_diagnosis, "sources": {}}

    output_file = os.path.join(merge_dir, str(file_name)+".json")
    async with aiofiles.open(output_file, "w") as f:
        await f.write(json.dumps(merged_diagnosis_dict, indent=4))
    inter_merge_logger.info(f"Saved merged diagnosis to: {output_file}")

    return merged_diagnosis_dict, module_names


async def run_async_inter_module_merge(module_diagnoses, config):
    inter_merge_logger.info("Starting inter-module merge process")
    root_path = get_root_path(config)
    inter_merge_dir = get_path([root_path, INTER_MODULE_MERGE_DIR])
    default_model = config["default_model"]
    if "inter_module_merge" in config["steps"]:
        model = config["steps"]["inter_module_merge"]["model"]
    else:
        model = default_model

    rag_enabled = config["RAG"]["enabled"]

    # split list into pairs and merge in parallel
    # if odd number of elements, last element is a singleton and will be merged in next step
    tasks = []
    merge_step = 1
    current_merge_dir = get_path([inter_merge_dir, merge_step])
    remaining_modules = list(module_diagnoses.keys())
    if not remaining_modules:
        return "No module diagnoses available for merging."

    if len(remaining_modules) < 2:
        return "No module diagnoses available for merging."
    while len(remaining_modules) > 2:
        inter_merge_logger.debug(
            f"Merge step {merge_step}, remaining modules: {len(remaining_modules)}")
        new_remaining_modules = []
        removed_modules = []
        for i in range(0, len(remaining_modules)-1, 2):
            module_1_name = remaining_modules[i]
            module_2_name = remaining_modules[i+1]

            diagnosis_1 = module_diagnoses[module_1_name]
            diagnosis_2 = module_diagnoses[module_2_name]

            merged = merge_diagnoses(diagnosis_1, diagnosis_2, config)
            return "No module diagnoses available for merging."
        module_1_name = remaining_modules[i]
        module_1_diagnosis = module_diagnoses[module_1_name]
        removed_modules.append(module_1_name)
        module_2_name = remaining_modules[i+1]
        module_2_diagnosis = module_diagnoses[module_2_name]
        removed_modules.append(module_2_name)
        combined_module_name = module_1_name+'_'+module_2_name
        new_remaining_modules.append(combined_module_name)
        if rag_enabled:
            tasks.append(merge_inter_module_diagnoses(model, default_model, [
                         module_1_name, module_2_name], module_1_diagnosis, module_2_diagnosis, combined_module_name, current_merge_dir))
        else:
            tasks.append(merge_inter_module_diagnoses(model, default_model, [
                         module_1_name, module_2_name], module_1_diagnosis, module_2_diagnosis, combined_module_name, current_merge_dir, rag_enabled=False))
        for module in removed_modules:
            module_diagnoses.pop(module)
            remaining_modules.remove(module)
        # if odd number of elements, last element is copied to next step
        if len(module_diagnoses) % 2 == 1:
            singleton_name = remaining_modules[0]
            new_remaining_modules.append(singleton_name)
            singleton_diagnosis = module_diagnoses[singleton_name]
            async with aiofiles.open(os.path.join(current_merge_dir, f"{singleton_name}.json"), "w") as f:
                await f.write(json.dumps(singleton_diagnosis, indent=4))
        else:
            singleton_diagnosis = None

        diagnosis_results = await asyncio.gather(*tasks)
        for result in diagnosis_results:
            module_diagnosis, module_names = result
            if len(module_names) > 1:
                module_names = '_'.join(module_names)
            else:
                module_names = module_names[0]
            module_diagnoses[module_names] = module_diagnosis
        if singleton_diagnosis is not None:
            module_diagnoses[singleton_name] = singleton_diagnosis
        remaining_modules = new_remaining_modules
        merge_step += 1

    final_diagnosis_dir = get_path([root_path, FINAL_DIAGNOSIS_DIR])
    inter_merge_logger.info("Performing final inter-module merge")
    module_1_name = remaining_modules[0]
    module_1_diagnosis = module_diagnoses[module_1_name]
    module_2_name = remaining_modules[1]
    module_2_diagnosis = module_diagnoses[module_2_name]
    module_names = module_1_name+'_'+module_2_name
    if rag_enabled:
        final_diagnosis, _ = await merge_inter_module_diagnoses(model, default_model, [module_1_name, module_2_name], module_1_diagnosis, module_2_diagnosis, FINAL_DIAGNOSIS_NAME, final_diagnosis_dir, final=True)
    else:
        final_diagnosis, _ = await merge_inter_module_diagnoses(model, default_model, [module_1_name, module_2_name], module_1_diagnosis, module_2_diagnosis, FINAL_DIAGNOSIS_NAME, final_diagnosis_dir, final=True, rag_enabled=False)
    inter_merge_logger.info("Completed inter-module merge process")
    return final_diagnosis


async def inter_module_merge(config):
    inter_merge_logger.info("Starting inter-module merge process")
    root_path = get_root_path(config)
    module_diagnoses_dir = get_path([root_path, FINAL_MODULE_MERGE_DIR])

    module_diagnoses = {}
    for file in os.listdir(module_diagnoses_dir):
        if ".json" not in file:
            continue
        module_name = file.split(".")[0]
        if module_name not in module_diagnoses:
            module_diagnoses[module_name] = {}
        file_path = os.path.join(module_diagnoses_dir, file)
        async with aiofiles.open(file_path, "r") as f:
            module_diagnoses[module_name] = json.loads(await f.read())

    final_diagnosis = await run_async_inter_module_merge(module_diagnoses, config)
    return final_diagnosis

if __name__ == "__main__":
    intra_merge_logger.info("Running pairwise_merge as main")
    inter_merge_logger.info("Running pairwise_merge as main")
    default_config = json.load(open(
        "/Users/chris/Documents/Github/IONPro/IONPro/Configs/default_config.json", "r"))

    intra_module_merge(default_config)
    inter_module_merge(default_config)
    intra_merge_logger.info("Completed pairwise_merge execution")
    inter_merge_logger.info("Completed pairwise_merge execution")
