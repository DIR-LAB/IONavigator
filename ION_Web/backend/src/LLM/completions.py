from litellm import completion, acompletion, token_counter
from litellm.exceptions import APIConnectionError
from LLM.metrics import count_completion, count_async_completion
import asyncio
import time
import os


class CompletionQueue:
    def __init__(self, rate_limit=None, tpm_limit=None):
        self.rate_limit = rate_limit  # requests per second
        self.tpm_limit = tpm_limit    # tokens per minute
        self.queue = asyncio.Queue()
        self.last_request_time = 0
        self.tokens_available = tpm_limit
        self.token_lock = asyncio.Lock()
        self.last_tokens_update = time.time()
        self.requests_completed = 0
        self.requests_made = 0
        self.requests_in_progress = 0
        self.last_log_time = time.time()
        self.max_retries = 5
        self.processing_task = None

    async def add_to_queue(self, coro_func, *args, **kwargs):
        if self.rate_limit and self.tpm_limit:
            self.requests_made += 1

            future = asyncio.Future()
            estimated_tokens = kwargs.pop("estimated_tokens", None)
            await self.queue.put((future, coro_func, args, kwargs, 0, estimated_tokens))
            if self.processing_task is None or self.processing_task.done():
                self.processing_task = asyncio.create_task(self.process_queue())
            return future
        else:
            raise Exception("Rate limit and TPM limit not set")

    async def update_tokens_available(self):
        current_time = time.time()
        elapsed = current_time - self.last_tokens_update
        tokens_to_add = (elapsed / 60) * self.tpm_limit
        self.tokens_available = min(self.tokens_available + tokens_to_add, self.tpm_limit)
        self.last_tokens_update = current_time

    async def process_queue(self):
        while True:
            try:
                future, coro_func, args, kwargs, retry_count, estimated_tokens = await self.queue.get()
                asyncio.create_task(self._handle_request(future, coro_func, args, kwargs, retry_count, estimated_tokens))
                self.queue.task_done()
                self.log_requests()
            except Exception as e:
                print(f"Error in process_queue: {e}")
                raise e

    async def _handle_request(self, future, coro_func, args, kwargs, retry_count, estimated_tokens):
        try:

            # Wait for tokens to be available
            while True:
                await self.update_tokens_available()
                async with self.token_lock:
                    if self.tokens_available >= estimated_tokens:
                        self.tokens_available -= estimated_tokens
                        break
                # Calculate time to wait before checking again
                tokens_needed = estimated_tokens - self.tokens_available
                time_to_wait = (tokens_needed / self.tpm_limit) * 60
                await asyncio.sleep(time_to_wait)
            
            # Enforce rate limit
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            sleep_time = max(0, (1 / self.rate_limit) - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            async with self.token_lock:
                self.last_request_time = time.time()

            # Proceed with the API call
            kwargs.pop("estimated_tokens", None)
            async with self.token_lock:
                self.requests_in_progress += 1
            response = await coro_func(*args, **kwargs)
            async with self.token_lock:
                self.requests_in_progress -= 1
            # Adjust tokens based on actual usage if possible
            actual_tokens_used = response._hidden_params.get("actual_tokens", estimated_tokens)
            token_diff = actual_tokens_used - estimated_tokens
            async with self.token_lock:
                self.tokens_available -= token_diff
            future.set_result(response)
        except Exception as e:
            # Handle retries
            if retry_count < self.max_retries:
                await self.queue.put((future, coro_func, args, kwargs, retry_count + 1, estimated_tokens))
            else:
                future.set_exception(e)
        finally:
            self.requests_completed += 1

    def log_requests(self):
        current_time = time.time()
        if current_time - self.last_log_time >= 1:
            self.requests_completed = 0
            self.last_log_time = current_time


COMPLETION_QUEUE = None
QUEUE_TASK = None

def get_completion_queue(rate_limit, tpm_limit):
    global COMPLETION_QUEUE
    global QUEUE_TASK
    loop = asyncio.get_event_loop()
    COMPLETION_QUEUE = CompletionQueue(rate_limit, tpm_limit)
    QUEUE_TASK = loop.create_task(COMPLETION_QUEUE.process_queue())
    return COMPLETION_QUEUE

def stop_completion_queue():
    global QUEUE_TASK
    if QUEUE_TASK:
        QUEUE_TASK.cancel()
        QUEUE_TASK = None

# regular completion
@count_completion
def generate_completion(model, messages, token_limit=None, retry=True, tools=None, full_message=False):
    input_tokens = token_counter(model=model, messages=messages)
    try:
        if token_limit:
            max_response_tokens = token_limit - input_tokens - 40
            if tools:
                response = completion(model=model, messages=messages, max_tokens=max_response_tokens, tools=tools, tool_choice='auto')
            else:
                response = completion(model=model, messages=messages, max_tokens=max_response_tokens)
        else:
            if tools:
                response = completion(model=model, messages=messages, tools=tools, tool_choice='auto')
            else:
                response = completion(model=model, messages=messages)
        cost = response._hidden_params["response_cost"]
    except (APIConnectionError, RuntimeError) as e:
        time.sleep(0.5)
        if retry:
            if tools:
                response = generate_completion(model, messages, token_limit, retry=False, tools=tools, full_message=full_message)
            else:
                response = generate_completion(model, messages, token_limit, retry=False, full_message=full_message)
        else:
            raise e
        cost = 0
        completion_result = {"model": model, "cost": cost, "response": response}
        return completion_result

    if full_message:
        completion_result = {"model": model, "cost": cost, "response": response.choices[0].message}
    else:
        completion_result = {"model": model, "cost": cost, "response": response.choices[0].message.content}
    return completion_result


#async completion
@count_async_completion
async def generate_async_completion(model, messages, token_limit=None, retry=True, tools=None, full_message=False):
    input_tokens = token_counter(model=model, messages=messages)
    try:
        if token_limit:
            max_response_tokens = token_limit - input_tokens - 40
            estimated_tokens = input_tokens + max_response_tokens
            if tools:
                response_future = await COMPLETION_QUEUE.add_to_queue(acompletion, model, messages, max_response_tokens, estimated_tokens=estimated_tokens, tools=tools, tool_choice='auto')
            else:
                response_future = await COMPLETION_QUEUE.add_to_queue(acompletion, model, messages, max_response_tokens, estimated_tokens=estimated_tokens)
        else:
            estimated_tokens = input_tokens + 1500
            if tools:
                response_future = await COMPLETION_QUEUE.add_to_queue(acompletion, model, messages, estimated_tokens=estimated_tokens, tools=tools, tool_choice='auto')
            else:
                response_future = await COMPLETION_QUEUE.add_to_queue(acompletion, model, messages, estimated_tokens=estimated_tokens)
        response = await response_future
        cost = response._hidden_params["response_cost"]
    except (APIConnectionError, RuntimeError) as e:
        time.sleep(0.5)
        if retry:
            if tools:
                response = await generate_async_completion(model, messages, token_limit, retry=False, tools=tools, tool_choice='auto', full_message=full_message)
            else:
                response = await generate_async_completion(model, messages, token_limit, retry=False, full_message=full_message)
        else:
            raise e
        cost = 0
        completion_result = {"model": model, "cost": cost, "response": response}
        return completion_result

    if full_message:
        completion_result = {"model": model, "cost": cost, "response": response.choices[0].message}
    else:
        completion_result = {"model": model, "cost": cost, "response": response.choices[0].message.content}
    return completion_result







