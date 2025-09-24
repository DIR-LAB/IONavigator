"""
Run IONPro against TraceBench traces (or a subset of traces), and save their results for later analysis
"""

import os
import subprocess
import json
import glob
from rich.console import Console
from rich.panel import Panel
import sys
import argparse
import copy
import asyncio
from pathlib import Path
import concurrent.futures
import itertools
from run_ion import load_rag_index, run_ION
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.core.response_synthesizers import ResponseMode

MODULES = ["IO500", "real_app_bench", "single_issue_bench"]

console = Console()


def get_trace_directories(
    trace_dir: str = "./evaluator/", traces_modules: list[str] = MODULES
):
    """Get all trace file paths to be evaluated

    Args:
        trace_dir (str, optional): directory that contains all of the traces from TraceBench. Defaults to './evaluator/'.
        traces_modules (list[str], optional): all of the modules to be evaluate within Tracebench. Defaults to all modules ("IO500", "real_app_bench", "single_issue_bench").

    Returns:
        tuple[list[str], list[str]]: absolute file paths of all traces to run ION on, names of all traces
    """
    trace_paths = []
    trace_names = []

    for module in traces_modules:
        trace_path_dir = Path(
            os.path.join(
                trace_dir, "TraceBench", "Datasets", module, "processed_traces"
            )
        )

        # We only want directories within this folder, ignore all others
        traces = [str(p.resolve()) for p in trace_path_dir.iterdir() if p.is_dir()]

        # Ensure that they are absolute file paths and not just references to specific directories
        trace_paths.extend(traces)
        trace_names.extend(list(map(lambda x: os.path.basename(x), traces)))

    return trace_paths, trace_names


# TODO: Run RAG Index at beginning and then run queries (deconstruct run.py essentially)
async def run_ion_analysis(
    trace: str,
    config_file: dict[str, str],
    model_file: dict[str, str],
    analysis_root: str,
    index,
) -> tuple[str, dict[str, str]] | None:
    """Run the ION analysis on a specific trace and return the result.

    Args:
        trace (str): The file path of the trace to be evaluated on.
        config_file (str): The path to the config file to use while running ION.
        analysis_root (str): The root directory where analysis outputs are stored.

    Returns:
        tuple[str, dict[str, str]] | None: A tuple containing the module and result dictionary, or None if analysis failed.
    """
    name = os.path.basename(trace)
    # Each trace needs its own config or otherwise we run into parallelism issues
    run_config = copy.deepcopy(config_file)
    run_config["trace_path"] = trace

    # Typically, we are running ION from within the ION folder, but because are doing so from TraceBench now, we need to modify our final output directory so that it still feels like it's being run from within the that directory
    # Ensure a unique per-trace analysis root to avoid collisions
    base_root = run_config.get("analysis_root", analysis_root)

    # If caller already prepended an absolute path keep it, else build one
    if not os.path.isabs(base_root):
        per_trace_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "ION", base_root)
        )
    else:
        per_trace_root = base_root
    run_config["analysis_root"] = per_trace_root

    console.print(
        Panel(
            f"Processing trace: [bold cyan]{name}[/bold cyan]",
            title="Trace Processing",
            expand=False,
            border_style="blue",
        )
    )

    console.print(f"[cyan][{name}][/cyan] Starting IONPro for [bold]{name}[/bold]...")
    try:
        final_diagnosis = await run_ION(run_config, model_file, index)
    except Exception as e:
        console.print(
            f"[red][{name}][/red] Exception while running ION: [bold red]{e}[/bold red]"
        )
        final_diagnosis = None
    console.print(f"[green][{name}][/green] Finished IONPro for [bold]{name}[/bold]")

    # consider the run successful if run_ION returned a diagnosis object
    if final_diagnosis is not None:
        console.print(
            f"[green]:heavy_check_mark: Successfully Ran IONavigator for {name}[/green]"
        )
        diagnosis_file = Path(
            os.path.join(
                "..",
                "ION",
                run_config["analysis_root"],
                name,
                "final_diagnosis",
                "final_diagnosis.json",
            )
        ).resolve()
        if os.path.exists(diagnosis_file):
            module = Path(trace).parent.parent.name

            if module not in MODULES:
                console.print(
                    f"[yellow]:warning: Directory structure for the traces does not follow regular format for {name}. Defaulting to 'other'."
                )
                module = "other"

            console.print(
                Panel(
                    f"The file is located at [medium_orchid][link=file://{diagnosis_file}]{diagnosis_file}[/link][/medium_orchid]",
                    title=f"Found diagnosis file for {name}",
                    expand=False,
                    border_style="purple",
                )
            )
            return module, {name: str(diagnosis_file)}
        else:
            console.print(
                f"[yellow]:warning: No diagnosis file found for {name} at {diagnosis_file}[/yellow]"
            )
            return None
    else:
        console.print(f"[red]:x: Analysis failed for {name}[/red]")
        return None


def main(**kwargs):
    """run ION against all traces"""
    # TODO: Change all of these print statements to logging statements eventually as well

    with open(kwargs["config"], "r") as f:
        config_file_data = json.load(f)
    with open(kwargs["models"], "r") as f:
        model_file_data = json.load(f)["models"]
    analysis_root = config_file_data["analysis_root"]

    if kwargs["modules"] == "all":
        traces, trace_names = get_trace_directories(kwargs["traces_path"], MODULES)
    else:
        traces, trace_names = get_trace_directories(
            kwargs["traces_path"], kwargs["modules"]
        )

    console.print("Trace paths to be processed:", traces)

    # Dictionary to store results
    results = {}

    # When we run the RAG diagnosis, reinitializing the Query Index again and Again can be very costly, so we do it once here
    if config_file_data["RAG"]["enabled"]:
        ion_dir = os.path.abspath(os.path.join("..", "ION", "ion"))
        rag_data_dir = os.path.join(
            ion_dir, config_file_data["RAG"]["rag_source_data_dir"]
        )
        rag_index_dir = os.path.join(ion_dir, config_file_data["RAG"]["rag_index_dir"])
        embedding_model = config_file_data["RAG"]["embedding_model"]
        reset_index = config_file_data["RAG"]["reset_index"]

        with console.status(
            f"[yellow]Initializing RAG index at: {rag_index_dir} (data: {rag_data_dir})...[/yellow]",
            spinner="dots",
        ):
            # TODO: Can we also have the CitationQueryEngine initialized here?
            QUERY_INDEX = load_rag_index(
                rag_data_dir=rag_data_dir,
                rag_index_dir=rag_index_dir,
                embedding_model=embedding_model,
                reset_index=reset_index,
            )
            QUERY_INDEX = CitationQueryEngine.from_args(
                QUERY_INDEX,
                similarity_top_k=10,
                max_top_k=10,
                response_mode=ResponseMode.NO_TEXT,
            )
    else:
        QUERY_INDEX = None
    console.print(
        f"[bold green]RAG index initialization complete: {rag_index_dir}[/bold green]"
    )

    # Run analyses concurrently in this process so we can pass the in-memory QUERY_INDEX
    async def _run_all():
        sem = asyncio.Semaphore(kwargs.get("concurrency", os.cpu_count()))

        async def _run_one(trace, name):
            async with sem:
                res = await run_ion_analysis(
                    trace, config_file_data, model_file_data, analysis_root, QUERY_INDEX
                )
                if res:
                    module, res_dict = res
                    results.setdefault(module, []).append(res_dict)

        tasks = [
            asyncio.create_task(_run_one(t, n)) for t, n in zip(traces, trace_names)
        ]
        if tasks:
            await asyncio.gather(*tasks)

    asyncio.run(_run_all())

    os.makedirs(kwargs["output"], exist_ok=True)
    output_json_path = Path(kwargs["output"], "trace_results.json").resolve()

    # If the file already exists, read the existing results and merge
    existing_results = {}
    if os.path.exists(output_json_path):
        with open(output_json_path, "r") as f:
            try:
                existing_results = json.load(f)
            except json.JSONDecodeError:
                console.print(
                    f"[yellow]Warning: Could not decode existing results file at {output_json_path}. It will be overwritten.[/yellow]"
                )

    # Merge new results into existing ones
    for module, res_list in results.items():
        if module not in existing_results:
            existing_results[module] = []

        # Create a map of existing names for quick lookup
        existing_names = {list(item.keys())[0] for item in existing_results[module]}
        for res in res_list:
            name = list(res.keys())[0]
            if name not in existing_names:
                existing_results[module].append(res)
            else:
                # Update existing entry
                for i, old_res in enumerate(existing_results[module]):
                    if list(old_res.keys())[0] == name:
                        existing_results[module][i] = res
                        break

    with open(output_json_path, "w") as f:
        json.dump(existing_results, f, indent=4)

    console.print(
        Panel(
            f"Results saved to [link=file://{output_json_path}]{output_json_path}[/link]",
            title="[bold green]Analysis Complete[/bold green]",
            subtitle="Output JSON",
            expand=False,
            border_style="green",
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TraceBench Analyzer: Run TraceBench Against a series of traces and save the result"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="../configs/default_config.json",
        help="Path to the configuration file",
    )
    parser.add_argument(
        "--models",
        type=str,
        default="../configs/models.json",
        help="Path to the models file",
    )
    parser.add_argument(
        "--traces_path",
        default="./evaluator/",
        type=str,
        help="Optionally set path to directory to extracted Tracebench traces. Defaults to ./evaluator/",
    )
    parser.add_argument(
        "--modules",
        nargs="+",
        default="all",
        choices=MODULES + ["all"],
        help="specify a specific module to run Tracebench against (choice either IO500, multi_issue_bench, single_issue_bench or real_app_bench)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="TraceBench_Output",
        help="Set the directory for analysis output. Defaults to ./TraceBench_Output",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=os.cpu_count(),
        help="Set the number of parallel processes to run. Defaults to the number of CPU cores.",
    )
    args = parser.parse_args()

    console.print(
        Panel(
            f"[bold]Configuration Arguments:[/bold]\n"
            f"Config File: {args.config}\n"
            f"Models File: {args.models}\n"
            f"Traces Path: {args.traces_path}\n"
            f"Modules: {args.modules}\n"
            f"Output Directory: {args.output}\n"
            f"Concurrency: {args.concurrency}",
            title="[b]Script Configuration[/b]",
            expand=False,
            border_style="magenta",
        )
    )

    # Run the entire analysis
    main(
        config=args.config,
        models=args.models,
        traces_path=args.traces_path,
        modules=args.modules,
        output=args.output,
        concurrency=args.concurrency,
    )
