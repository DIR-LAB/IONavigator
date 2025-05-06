import argparse
import asyncio
from ion.Utils import get_config, get_metrics, get_models
from ion.Completions import get_router
from ion import (
    run_ION, 
    set_rag_dirs,
    get_config,
    get_metrics,
    )


async def main():
    parser = argparse.ArgumentParser(description="IONPro: Intelligent Diagnosis of I/O Performance Issues")
    parser.add_argument("--config", type=str, default="../configs/default_config.json", help="Path to the configuration file")
    parser.add_argument("--models", type=str, default="../configs/models.json", help="Path to the models file")
    parser.add_argument("--trace_path", type=str, help="Optionally set path to the Darshan trace file from command line (overrides config)")
    args = parser.parse_args()

    # get config
    config = get_config(args.config)
    models = get_models(args.models)
    get_router(models)

    if args.trace_path:
        config["trace_path"] = args.trace_path
    
    # set rate limit
    config = set_rag_dirs(config)
    
    final_diagnosis = await run_ION(config, format_md = True)

    print("final metrics: ", get_metrics())


if __name__ == "__main__":
    
    asyncio.run(main())