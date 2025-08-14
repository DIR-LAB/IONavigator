# from TraceBench.Scripts.Utils import get_label_codes, format_messages
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ION"))
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
from rich.columns import Columns

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
    file_path = validate_file_path(file_path=file_path, error_msg=error_msg)

    with open(file_path, "r") as f:
        data = json.load(f)

    return data


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
        with console.status(
            f"[cyan]Evaluating trace: {sample['trace_name']}...[/cyan]"
        ) as status:
            sample_results = await eval_sample(
                bench_root=bench_root, sample=sample, labels=labels, model=eval_model
            )
        console.print(
            f"[bold green]Finished evaluating trace: {sample['trace_name']}[/bold green]"
        )

        # TODO: Create per trace visualizations of the performance

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

    result_text = ""
    result_text += f"[gray]True Positives[/gray]: [bold]{total_tp}[/bold]\n"
    result_text += f"[gray]True Negatives[/gray]: [bold]{total_tn}[/bold]\n"
    result_text += f"[gray]False Positives[/gray]: [bold]{total_fp}[/bold]\n"
    result_text += f"[gray]False Negatives[/gray]: [bold]{total_fn}[/bold]\n"
    result_text += f"[green]Total Results[/green]: [bold]{total_results}[/bold]\n"
    result_text += f"[gray]Precision[/gray]: [bold]{precision:.2f}[/bold]\n"
    result_text += f"[gray]Recall[/gray]: [bold]{recall:.2f}[/bold]\n"
    result_text += f"[gray]F1 Score[/gray]: [bold]{f1:.2f}[/bold]\n"
    result_text += f"[gray]Accuracy[/gray]: [bold]{accuracy:.2f}[/bold]\n"
    console.print(
        Panel(
            result_text,
            title="Final Metric Results",
            expand=False,
            border_style="green",
        )
    )

    label_panels = []
    for label in per_label_results:
        label_result = per_label_results[label]
        label_text = (
            f"[gray]Precision[/gray]: [bold]{label_result['precision']:.2f}[/bold]\n"
            f"[gray]Recall[/gray]: [bold]{label_result['recall']:.2f}[/bold]\n"
            f"[gray]F1 Score[/gray]: [bold]{label_result['f1']:.2f}[/bold]\n"
            f"[gray]Accuracy[/gray]: [bold]{label_result['accuracy']:.2f}[/bold]\n"
            f"[gray]True Positives[/gray]: [bold]{label_result['total_tp']}[/bold]\n"
            f"[gray]True Negatives[/gray]: [bold]{label_result['total_tn']}[/bold]\n"
            f"[gray]False Positives[/gray]: [bold]{label_result['total_fp']}[/bold]\n"
            f"[gray]False Negatives[/gray]: [bold]{label_result['total_fn']}[/bold]\n"
            f"[green]Total Results[/green]: [bold]{label_result['total_results']}[/bold]\n"
        )
        label_panels.append(
            Panel(
                label_text, title=f"[b]{label}[/b]", expand=False, border_style="blue"
            )
        )

    overall_panel = Panel(
        Columns(label_panels, expand=True),
        title="[b]Label Specific Metrics[/b]",
        expand=True,
        border_style="cyan",
    )
    console.print(overall_panel)

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
    config: str = load_json(
        kwargs["config"], f"Could not locate the config directory: {kwargs['config']}"
    )
    traces_path: str = validate_file_path(
        os.path.join(kwargs["traces_path"], "TraceBench"),
        f"Could not locate the Trace Path Directory: {kwargs['traces_path']}",
    )
    traces_result: str = load_json(
        kwargs["traces_results"],
        f"Could not locate the Trace Result JSON File: {kwargs['traces_results']}",
    )
    output_dir: str = kwargs["output"]
    sample_dicts: dict[str, dict[str | list[str]]] = {}

    os.makedirs(output_dir, exist_ok=True)

    module_dataset_labels: dict[str, dict[str, str]] = {}
    trace_dataset_labels: dict[str, list[str]] = {}

    for module in traces_result:
        module_path: str = os.path.join(
            traces_path, "Datasets", module, "trace_labels.json"
        )
        module_labels: dict[str, str] = module_dataset_labels.setdefault(
            module,
            load_json(
                module_path,
                f"Could not find a valid module directory in the TraceBench directory for {module}: {module_path}",
            ),
        )
        for trace_name, trace_diagnosis_path in [
            tuple(item.items())[0] for item in traces_result[module]
        ]:
            trace_dict = sample_dicts.setdefault(trace_name, {"trace_name": trace_name})
            trace_dict["labels"] = module_labels[trace_name]
            trace_diagnosis: dict[str, str] = load_json(
                trace_diagnosis_path,
                f"Could not the Final Diagnosis JSON File for {trace_name}: {trace_diagnosis_path}",
            )
            trace_dict["generated_summary"] = trace_diagnosis["diagnosis"]
            trace_dict["source_dir"] = os.path.join(
                traces_path, "Datasets", module, "processed_traces", trace_name
            )

            sample_dicts[trace_name] = trace_dict

    issue_definitions: dict[str, dict[str, str]] = load_json(
        os.path.join(traces_path, "Dataset_Labels.json"),
        f"Could not find the Issue Descriptions within the TraceBench Folder: {os.path.join(traces_path, "Dataset_Labels.json")}",
    )
    sample_list: list[dict[str, str | list[str]]] = list(sample_dicts.values())

    console.print(
        f"[bold green]Evaluation is about to begin![/bold green][bold] {len(sample_list)}[/bold] traces will be evaluated.\n"
    )
    eval_results = await eval_sample_set(
        bench_root=os.path.join(traces_path, "Datasets"),
        completed_samples=sample_list,
        labels=issue_definitions,
        eval_model=config["default_model"],
    )

    quantified_eval_results = quantify_eval_results(eval_results)

    final_results_path = os.path.join(output_dir, "evaluation_results.json")
    with open(final_results_path, "w") as f:
        json.dump(quantified_eval_results, f, indent=4)


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
        default="../configs/models.json",
        help="Path to the models file. Defaults to ../configs/models/json",
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

    get_router(
        load_json(
            args.models,
            f"Could not successfully load the models dictionary: {args.models}",
        )["models"]
    )

    # Run the entire analysis
    await run_evaluation(
        config=args.config,
        traces_path=args.traces_path,
        traces_results=args.traces_results,
        output=args.output,
    )


if __name__ == "__main__":
    asyncio.run(main())
