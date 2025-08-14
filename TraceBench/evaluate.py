# from TraceBench.Scripts.Utils import get_label_codes, format_messages
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ION'))
print(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ion.Completions import generate_async_completion, get_router
from prompts import format_messages
import asyncio
from rich.console import Console
from rich.panel import Panel
import argparse
from pathlib import Path
import json
from typing import Callable, Any

import re

# TODO: When we modify the structure for TraceBench, we will want to update these paths
COMPLETED_SAMPLES_FILE = "./"

console = Console()

"""
    Overall structure of what needs to be done:
    - Retrieve ground-truth labels for each trace (housed within respective module folders under trace_labels.json)
    - Retrieve the Dataset Labels (Definitions) from Dataset_Labels.json (housed within the root eval folder)
    - Leverage eval_sample as a guide on how to get prompt the LLM to get the TP, FP, TN, FN from the responses
        - bench_root is the path to the root of the benchmark dataset (probably eval/Datasets/ in this case)
        - sample is a dict that includes
            - the summary (generated_summary)
            - labels that is a list of the ground-truth (labels)
            - the source directory in which the trace comes from (source_dir)
            - the name of the trace (trace_name)
        - eval model, which we can likely just extract from the config file

"""


def validate_file_path(file_path: str, error_msg: str) -> str | FileNotFoundError:
    file_path = Path(file_path).resolve()

    if os.path.exists(file_path):
        return file_path
    else:
        raise FileNotFoundError(error_msg)
    
def load_json(file_path, error_msg: str) -> dict[Any, Any] | FileNotFoundError:
    file_path = validate_file_path(file_path = file_path, error_msg=error_msg)

    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data

async def eval_ranking_set(samples, model, bench_root):
    label_codes = get_label_codes(bench_root)
    completed_samples = {}
    criterium = ["Accuracy", "Utility", "Interpretability"]

    async def process_sample(sample):
        print("\n\n")
        print("sample: ", sample)
        print("\n\n")
        sample_result = {}
        for criteria in criterium:
            sample_result[criteria] = {}
            for rotate_by in range(4):

                sample_labels = {
                    label_codes[label]["Title"]: label_codes[label]["Description"]
                    for label in sample["labels"]
                }
                kwargs = {
                    "rank_criteria": criteria,
                    "labels": sample_labels,
                    "rotate_by": rotate_by,
                }
                if sample["drishti_diagnosis"] == "":
                    kwargs["Drishti_diagnosis"] = "Diagnosis failed."
                else:
                    kwargs["Drishti_diagnosis"] = sample["drishti_diagnosis"]
                if sample["ion_diagnosis"] == "":
                    kwargs["ION1_diagnosis"] = "Diagnosis failed."
                else:
                    kwargs["ION1_diagnosis"] = sample["ion_diagnosis"]
                if sample["ion2_diagnosis"] == "":
                    kwargs["ION2_diagnosis"] = "Diagnosis failed."
                else:
                    kwargs["ION2_diagnosis"] = sample["ion2_diagnosis"]
                if kwargs["ION2_diagnosis"] == "Diagnosis failed.":
                    kwargs["ION2_Llama_diagnosis"] = "Diagnosis failed."
                else:
                    kwargs["ION2_Llama_diagnosis"] = sample["ion2_llama_diagnosis"]
                messages = format_messages("compare_diagnoses", kwargs)
                response = await generate_async_completion(model, messages)
                tool_ranks, explanation = extract_rank_response_content(response)
                if rotate_by == 0:
                    sample_result[criteria]["ION2_rank"] = int(tool_ranks[0])
                    sample_result[criteria]["ION1_rank"] = int(tool_ranks[1])
                    sample_result[criteria]["drishti_rank"] = int(tool_ranks[2])
                    sample_result[criteria]["ION2_Llama_rank"] = int(tool_ranks[3])

                else:
                    sample_result[criteria]["ION2_rank"] += int(tool_ranks[0])
                    sample_result[criteria]["ION1_rank"] += int(tool_ranks[1])
                    sample_result[criteria]["drishti_rank"] += int(tool_ranks[2])
                    sample_result[criteria]["ION2_Llama_rank"] += int(tool_ranks[3])
                sample_result[criteria][f"explanation_{rotate_by}"] = explanation
                tool_ranks_str = [
                    f"{tool}: {rank}"
                    for tool, rank in zip(
                        ["ION-2", "Drishti", "ION-1", "ION-2 Llama"], tool_ranks
                    )
                ]
                print(f"Ranked Diagnoses based on {criteria}: {tool_ranks_str}")
                print(f"Explanation: {explanation}")
        print("\n\n\n")
        return sample["source_dir"], sample["trace_name"], sample_result

    tasks = [process_sample(sample) for sample in samples]
    results = await asyncio.gather(*tasks)

    for source_dir, trace_name, result in results:
        if source_dir not in completed_samples:
            completed_samples[source_dir] = {}
        completed_samples[source_dir][trace_name] = result

    return completed_samples


def quantify_ranking_results(eval_results):
    quantified_results = {
        "Overall": {
            "Accuracy": {"Drishti": 0, "ION-1": 0, "ION-2": 0, "ION-2 Llama": 0},
            "Utility": {"Drishti": 0, "ION-1": 0, "ION-2": 0, "ION-2 Llama": 0},
            "Interpretability": {
                "Drishti": 0,
                "ION-1": 0,
                "ION-2": 0,
                "ION-2 Llama": 0,
            },
            "Total": {"Drishti": 0, "ION-1": 0, "ION-2": 0, "ION-2 Llama": 0},
        }
    }

    for source_dir in eval_results:
        quantified_results[source_dir] = {
            "Accuracy": {"Drishti": 0, "ION-1": 0, "ION-2": 0, "ION-2 Llama": 0},
            "Utility": {"Drishti": 0, "ION-1": 0, "ION-2": 0, "ION-2 Llama": 0},
            "Interpretability": {
                "Drishti": 0,
                "ION-1": 0,
                "ION-2": 0,
                "ION-2 Llama": 0,
            },
            "Total": {"Drishti": 0, "ION-1": 0, "ION-2": 0, "ION-2 Llama": 0},
        }

        total_samples = len(eval_results[source_dir])

        for sample in eval_results[source_dir].values():
            for criterion in ["Accuracy", "Utility", "Interpretability"]:
                for tool, rank_key in [
                    ("Drishti", "drishti_rank"),
                    ("ION-1", "ION1_rank"),
                    ("ION-2", "ION2_rank"),
                    ("ION-2 Llama", "ION2_Llama_rank"),
                ]:
                    score = 16 - sample[criterion][rank_key]
                    quantified_results[source_dir][criterion][tool] += score
                    quantified_results["Overall"][criterion][tool] += score

        # Normalize scores for this source_dir
        for criterion in ["Accuracy", "Utility", "Interpretability"]:
            for tool in ["Drishti", "ION-1", "ION-2", "ION-2 Llama"]:
                quantified_results[source_dir][criterion][tool] /= (
                    12 * total_samples
                )  # Max score per sample is 3
                quantified_results[source_dir]["Total"][tool] += quantified_results[
                    source_dir
                ][criterion][tool]

        # Calculate total average for this source_dir
        for tool in ["Drishti", "ION-1", "ION-2", "ION-2 Llama"]:
            quantified_results[source_dir]["Total"][tool] /= 3  # Average of 3 criteria

    # Calculate overall scores
    total_samples = sum(len(samples) for samples in eval_results.values())
    for criterion in ["Accuracy", "Utility", "Interpretability"]:
        for tool in ["Drishti", "ION-1", "ION-2", "ION-2 Llama"]:
            quantified_results["Overall"][criterion][tool] /= 12 * total_samples
            quantified_results["Overall"]["Total"][tool] += quantified_results[
                "Overall"
            ][criterion][tool]

    # Calculate overall average
    for tool in ["Drishti", "ION-1", "ION-2", "ION-2 Llama"]:
        quantified_results["Overall"]["Total"][tool] /= 3  # Average of 3 criteria

    return quantified_results


def extract_response_content(prompt_type, response):
    if prompt_type == "check_no_issue":
        # Result: <Result of the check; must be either 'No issues identified' or 'False Positives Identified'>
        # List of False Positives: <List of false positives identified by the tool, if any>
        match = re.search(r"Result:\s*(.*)", response)
        if match:
            binary_eval = match.group(1)
            if "No issues identified" in binary_eval:
                return True, None
            else:
                match = re.search(r"List of False Positives:\s*(.*)", response)
                if match:
                    false_positives = match.group(1)
                    return False, false_positives
                else:
                    return None, None
        else:
            raise ValueError("Invalid response format: {}".format(response))
    else:
        # Summary Report Identifies Issue: <yes or no>
        # Explanation: <explanation for your answer>
        match = re.search(r"summary report identifies issue:\s*(.*)", response.lower())
        if match:

            binary_eval = match.group(1)
            if "yes" in binary_eval.lower():
                binary_eval = True
            else:
                binary_eval = False
            match = re.search(r"Explanation:\s*(.*)", response)
            explanation = match.group(1)
            return binary_eval, explanation
        else:
            raise ValueError("Invalid response format: {}".format(response))


async def eval_sample(bench_root, sample, labels, model):
    generated_summary = sample["generated_summary"]
    sample_labels = sample["labels"]
    source_dir = sample["source_dir"]
    trace_name = sample["trace_name"]
    eval_results = []
    if len(sample_labels) == 1 and sample_labels[0] == "NOL":
        print("sample_labels: ", sample_labels)
        prompt_type = "check_no_issue"
        eval_kwargs = {"summary_report": generated_summary}
        messages = format_messages(prompt_type, eval_kwargs)
        response = await generate_async_completion(model, messages)
        eval_result = extract_response_content(prompt_type, response)
        eval_results.append(
            {
                "source_dir": source_dir,
                "trace_name": trace_name,
                "eval_result": eval_result,
                "label": "NOL",
                "ground_truth": True,
            }
        )
    else:
        tasks = []
        labels_to_eval = []
        ground_truth_labels = []
        for label in labels:
            if label == "NOL":
                continue
            if label in sample_labels:
                prompt_type = "check_issue"
                ground_truth = True
            else:
                prompt_type = "check_false_positive"
                ground_truth = False
            eval_kwargs = {
                "summary_report": generated_summary,
                "issue_name": labels[label]["Title"],
                "issue_description": labels[label]["Description"],
            }
            messages = format_messages(prompt_type, eval_kwargs)
            new_task = asyncio.create_task(generate_async_completion(model, messages))
            tasks.append(new_task)
            labels_to_eval.append((label, ground_truth))

        responses = await asyncio.gather(*tasks)
        for response, label in zip(responses, labels_to_eval):
            eval_result = extract_response_content(prompt_type, response)
            eval_results.append(
                {
                    "source_dir": source_dir,
                    "trace_name": trace_name,
                    "eval_result": eval_result,
                    "label": label[0],
                    "ground_truth": label[1],
                }
            )

    return eval_results


async def eval_sample_set(bench_root, completed_samples, labels, eval_model):
    eval_results = []
    for sample in completed_samples:
        with console.status(f"[cyan]Evaluating trace: {sample['trace_name']}...[/cyan]") as status:
            sample_results = await eval_sample(bench_root=bench_root, sample=sample, labels=labels, model=eval_model)
        console.print(f"[bold green]Finished evaluating trace: {sample['trace_name']}[/bold green]")
        eval_results.append(sample_results)
    return eval_results


def quantify_eval_results(eval_results):
    per_label_results = {}
    total_tp, total_tn, total_fp, total_fn = 0, 0, 0, 0

    for sample in eval_results:
        for result in sample:
            label = result["label"]
            if label not in per_label_results:
                per_label_results[label] = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}

            eval_result = result["eval_result"][0]
            ground_truth = result["ground_truth"]

            if eval_result and ground_truth:
                per_label_results[label]["tp"] += 1
                total_tp += 1
            elif not eval_result and not ground_truth:
                per_label_results[label]["tn"] += 1
                total_tn += 1
            elif eval_result and not ground_truth:
                per_label_results[label]["fp"] += 1
                total_fp += 1
            else:
                per_label_results[label]["fn"] += 1
                total_fn += 1

    total_results = total_tp + total_tn + total_fp + total_fn

    # Calculate overall metrics
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )
    accuracy = (total_tp + total_tn) / total_results if total_results > 0 else 0

    for label in per_label_results:
        label_precision = (
            per_label_results[label]["tp"]
            / (per_label_results[label]["tp"] + per_label_results[label]["fp"])
            if (per_label_results[label]["tp"] + per_label_results[label]["fp"]) > 0
            else 0
        )
        label_recall = (
            per_label_results[label]["tp"]
            / (per_label_results[label]["tp"] + per_label_results[label]["fn"])
            if (per_label_results[label]["tp"] + per_label_results[label]["fn"]) > 0
            else 0
        )
        label_f1 = (
            2 * (label_precision * label_recall) / (label_precision + label_recall)
            if (label_precision + label_recall) > 0
            else 0
        )
        label_accuracy = (
            (per_label_results[label]["tp"] + per_label_results[label]["tn"])
            / (
                per_label_results[label]["tp"]
                + per_label_results[label]["tn"]
                + per_label_results[label]["fp"]
                + per_label_results[label]["fn"]
            )
            if (
                per_label_results[label]["tp"]
                + per_label_results[label]["tn"]
                + per_label_results[label]["fp"]
                + per_label_results[label]["fn"]
            )
            > 0
            else 0
        )
        per_label_results[label]["precision"] = label_precision
        per_label_results[label]["recall"] = label_recall
        per_label_results[label]["f1"] = label_f1
        per_label_results[label]["accuracy"] = label_accuracy
        per_label_results[label]["total_tp"] = per_label_results[label]["tp"]
        per_label_results[label]["total_tn"] = per_label_results[label]["tn"]
        per_label_results[label]["total_fp"] = per_label_results[label]["fp"]
        per_label_results[label]["total_fn"] = per_label_results[label]["fn"]
        per_label_results[label]["total_results"] = (
            per_label_results[label]["tp"]
            + per_label_results[label]["tn"]
            + per_label_results[label]["fp"]
            + per_label_results[label]["fn"]
        )

    print(f"True Positives: {total_tp}")
    print(f"True Negatives: {total_tn}")
    print(f"False Positives: {total_fp}")
    print(f"False Negatives: {total_fn}")
    print(f"Total Results: {total_results}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")
    print(f"Accuracy: {accuracy:.2f}")
    print("Per Label Results:")
    for label in per_label_results:
        print(
            f"{label}: Precision: {per_label_results[label]['precision']:.2f}, "
            f"Recall: {per_label_results[label]['recall']:.2f}, "
            f"F1 Score: {per_label_results[label]['f1']:.2f}, "
            f"Accuracy: {per_label_results[label]['accuracy']:.2f}, "
            f"Total TP: {per_label_results[label]['total_tp']}, "
            f"Total TN: {per_label_results[label]['total_tn']}, "
            f"Total FP: {per_label_results[label]['total_fp']}, "
            f"Total FN: {per_label_results[label]['total_fn']}, "
            f"Total Results: {per_label_results[label]['total_results']}"
        )

    return (
        per_label_results,
        total_tp,
        total_tn,
        total_fp,
        total_fn,
        total_results,
        precision,
        recall,
        f1,
    )


async def run_evaluation(**kwargs):
    config: str = load_json(kwargs['config'], f'Could not locate the config directory: {kwargs['config']}')
    traces_path: str = validate_file_path(os.path.join(kwargs["traces_path"], "TraceBench"), f"Could not locate the Trace Path Directory: {kwargs['traces_path']}")
    traces_result: str = load_json(kwargs['traces_results'], f"Could not locate the Trace Result JSON File: {kwargs['traces_results']}")
    output_dir: str = kwargs["output"]
    sample_dicts: dict[str, dict[str | list[str]]] = {}

    os.makedirs(output_dir, exist_ok=True)

    module_dataset_labels: dict[str, dict[str, str]] = {}
    trace_dataset_labels: dict[str, list[str]] = {}

    for module in traces_result:
        module_path: str = os.path.join(traces_path, "Datasets", module, "trace_labels.json")
        module_labels: dict[str, str] = module_dataset_labels.setdefault(module, load_json(module_path, f"Could not find a valid module directory in the TraceBench directory for {module}: {module_path}"))
        for trace_name, trace_diagnosis_path in [tuple(item.items())[0] for item in traces_result[module]]:
            trace_dict = sample_dicts.setdefault(trace_name, {'trace_name': trace_name})
            trace_dict['labels'] = module_labels[trace_name]
            trace_diagnosis: dict[str, str] = load_json(trace_diagnosis_path, f"Could not the Final Diagnosis JSON File for {trace_name}: {trace_diagnosis_path}")
            trace_dict["generated_summary"] = trace_diagnosis['diagnosis']
            trace_dict['source_dir'] = os.path.join(traces_path, "Datasets", module, "processed_traces", trace_name)

            sample_dicts[trace_name] = trace_dict

    issue_definitions: dict[str, dict[str, str]] = load_json(os.path.join(traces_path, "Dataset_Labels.json"), f"Could not find the Issue Descriptions within the TraceBench Folder: {os.path.join(traces_path, "Dataset_Labels.json")}")
    sample_list: list[dict[str, str | list[str]]] = list(sample_dicts.values())

    console.print(
        f"[bold green]Evaluation is about to begin![/bold green][bold] {len(sample_list)}[/bold] traces will be evaluated.\n"
    )
    eval_results = await eval_sample_set(bench_root=os.path.join(traces_path, "Datasets"), completed_samples=sample_list, labels=issue_definitions, eval_model=config['default_model'])





async def get_eval_results(eval_model, bench_root):
    with open(COMPLETED_SAMPLES_FILE, "r") as f:
        completed_samples = json.load(f)
    completed_samples = refresh_sample_labels(completed_samples, bench_root)
    eval_results = await eval_sample_set(bench_root, completed_samples, eval_model)
    return eval_results


async def main():
    parser = argparse.ArgumentParser(
        description="TraceBench Evaluator: Evaluate the results of the IONPro analysis with heuristic and LLM-based metrics"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="../configs/default_config.json",
        help="Path to the configuration file. Defaults to ../configs/default_config.json",
    )
    parser.add_argument(
        "--models",
        type=str,
        default = "../configs/models.json",
        help = "Path to the models file. Defaults to ../configs/models/json"
    )
    parser.add_argument(
        "--traces_path",
        type=str,
        default="./evaluator",
        help="Set path to directory to extracted Tracebench traces. Defaults to ./evaluator",
    )

    parser.add_argument(
        "--traces_results",
        default="./TraceBench_Output/trace_results.json",
        type=str,
        help="JSON file that lists a series of filepaths to various final diagnosis outputs generated by IONPro. Defaults to ./TraceBench_Output/trace_results.json",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="TraceBench_Output",
        help="Set the directory for analysis output. Defaults to ./TraceBench_Output",
    )
    args = parser.parse_args()

    console.print(
        Panel(
            f"[bold]Configuration Arguments:[/bold]\n"
            f"Config File: {args.config}\n"
            f"Models File: {args.models}\n"
            f"Traces Path: {args.traces_path}\n"
            f"Traces Results Path: {args.traces_results}\n"
            f"Output Directory: {args.output}",
            title="[b]Script Configuration[/b]",
            expand=False,
            border_style="magenta",
        )
    )

    get_router(load_json(args.models, f"Could not successfully load the models dictionary: {args.models}")['models'])

    # Run the entire analysis
    await run_evaluation(
        config=args.config,
        traces_path=args.traces_path,
        traces_results=args.traces_results,
        output=args.output,
    )


if __name__ == "__main__":
    asyncio.run(main())
