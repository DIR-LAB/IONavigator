import argparse
import asyncio
from ion.Utils import get_config, get_metrics
from ion.Completions import get_completion_queue, stop_completion_queue
from ion import (
    run_ION, 
    set_rag_dirs,
    get_config,
    get_metrics,
    get_completion_queue,
    stop_completion_queue
    )


async def main():
    parser = argparse.ArgumentParser(description="IONPro: Intelligent Diagnosis of I/O Performance Issues")
    parser.add_argument("--config", type=str, default="../Configs/default_config.json", help="Path to the configuration file")
    parser.add_argument("--trace_path", type=str, help="Optionally set path to the Darshan trace file from command line (overrides config)")
    args = parser.parse_args()

    # get config
    config = get_config(args.config)
    if args.trace_path:
        config["trace_path"] = args.trace_path
    
    # set rate limit
    get_completion_queue(config["rate_limit"], config["tpm_limit"])
    config = set_rag_dirs(config)
    
    final_diagnosis = await run_ION(config)

    print("final metrics: ", get_metrics())

    stop_completion_queue()

if __name__ == "__main__":
    
    asyncio.run(main())