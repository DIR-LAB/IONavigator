'''
    Run IONPro against TraceBench traces (or a subset of traces), and save their results for later analysis
'''

import os
import subprocess
import json
import glob
from rich.console import Console
from rich.panel import Panel
import sys
import argparse
from pathlib import Path

MODULES = ["IO500", "real_app_bench", "single_issue_bench"]

# Initialize Rich Console globally
console = Console()

def get_trace_directories(trace_dir, traces_modules):
    """Get all trace file paths to be evaluated"""
    trace_paths = []
    trace_names = []

    for module in traces_modules:
        trace_path_dir = Path(os.path.join(trace_dir, 'TraceBench', 'Datasets', module, 'processed_traces'))

        # We only want directories within this folder, ignore all others
        traces = [str(p.resolve()) for p in trace_path_dir.iterdir() if p.is_dir()]

        # Ensure that they are absolute file paths and not just references to specific directories 
        trace_paths.extend(traces)
        trace_names.extend(list(map(lambda x: os.path.basename(x), traces)))

    return trace_paths, trace_names

def run_ion_analysis(trace, config_file):
    """Run the ION analysis on a specific trace and ensure output lands in ION/ION_Output"""

    # TODO: Change this a parallel process potentially that can speed up the execution of many traces at once?
    result = subprocess.run([sys.executable, 'run.py', "--config", config_file, '--trace_path', trace], 
                           capture_output=False, text=True, cwd = '../ION/')

    
    return result.returncode == 0

def main(**kwargs):
    #TODO: Change all of these print statements to logging statements eventually and also rich print statements for the console
    # ion_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ION')

    with open(kwargs['config'], 'r') as f:
        config_file = json.load(f)
    analysis_root = config_file['analysis_root']
    

    if kwargs['modules'] == 'all':
        traces, trace_names = get_trace_directories(kwargs['traces_path'], MODULES)
    else:
        traces, trace_names = get_trace_directories(kwargs['traces_path'], kwargs['modules'])

    console.print("Trace paths to be processed:", traces)

    
    # # Dictionary to store results
    results = {}
    
    # Process each trace
    for trace, name in zip(traces, trace_names):
        console.print(Panel(f"Processing trace: [bold cyan]{name}[/bold cyan]", title="Trace Processing", expand=False, border_style="blue"))
        
        # Run ION analysis
        success = run_ion_analysis(trace, kwargs['config'])
        
        if success:
            console.print(f"[green]:heavy_check_mark: Successfully Ran IONavigator for {name}[/green]")
            # Find the diagnosis file
            diagnosis_file = Path(os.path.join('..', 'ION', analysis_root, name, 'final_diagnosis', 'final_diagnosis.json')).resolve()
            if os.path.exists(diagnosis_file):
                results[name] = str(diagnosis_file)
                console.print(f"[purple]Found diagnosis file: [link=file://{diagnosis_file}]{diagnosis_file}[/link][/purple]")
            else:
                console.print(f"[yellow]:warning: No diagnosis file found for {name} at {diagnosis_file}[/yellow]")
        else:
            console.print(f"[red]:x: Analysis failed for {name}[/red]")
    
    # Save results to JSON file
    os.makedirs(kwargs['output'], exist_ok = True)
    output_json_path = Path(kwargs['output'], 'trace_results.json').resolve()
    with open(output_json_path, 'w') as f:
        # TODO: We might want to modify this so that existing trace runs / paths are not entirely removed but just ones with the same keys are overridden with the new file path values 
        json.dump(results, f, indent=4)
    
    console.print(Panel(f"Results saved to [link=file://{output_json_path}]{output_json_path}[/link]", title="[bold green]Analysis Complete[/bold green]", subtitle="Output JSON", expand=False, border_style="green"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TraceBench Analyzer: Run TraceBench Against a series of traces and save the result")
    parser.add_argument("--config", type=str, default="../configs/default_config.json", help="Path to the configuration file")
    parser.add_argument("--traces_path", default = './evaluator/', type=str, help="Optionally set path to directory to extracted Tracebench traces. Defaults to ./evaluator/")
    parser.add_argument('--modules', nargs='+', default = 'all', choices = MODULES, help = 'specify a specific module to run Tracebench against (choice either IO500, multi_issue_bench, single_issue_bench or real_app_bench)')
    parser.add_argument('--output', type = str, default = 'TraceBench_Output', help = 'Set the directory for analysis output. Defaults to ./TraceBench_Output')
    args = parser.parse_args()

    console.print(Panel(f"[bold]Configuration Arguments:[/bold]\n"
                        f"Config File: {args.config}\n"
                        f"Traces Path: {args.traces_path}\n"
                        f"Modules: {args.modules}\n"
                        f"Output Directory: {args.output}",
                        title="[b]Script Configuration[/b]", expand=False, border_style="magenta"))


    # Run the entire analysis
    main(config = args.config, traces_path = args.traces_path, modules = args.modules, output = args.output)

