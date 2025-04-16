import functools
import asyncio
import time


metrics = {
    'models':{},
    "total_completions": 0,
    "completion_time": 0,
    "total_cost": 0,
    "runtime": 0
}


def add_completion(model, cost):
    if model not in metrics["models"]:
        metrics["models"][model] = {
            "completions": 0,
            "cost": 0
        }
    metrics["models"][model]["completions"] += 1
    if cost is not None:
        metrics["models"][model]["cost"] += cost
        metrics["total_cost"] += cost
    metrics["total_completions"] += 1

def count_completion(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        metrics["completion_time"] += end_time - start_time
        add_completion(result["model"], result["cost"])
        return result["response"]
    return wrapper

def count_async_completion(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        metrics["completion_time"] += end_time - start_time
        add_completion(result["model"], result["cost"])
        return result["response"]
    return async_wrapper

def count_runtime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        metrics[f"{func.__name__}_runtime"] = end_time - start_time
        return result
    return wrapper

def get_metrics():
    return metrics






