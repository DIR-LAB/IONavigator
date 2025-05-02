from litellm import completion, acompletion, token_counter
from litellm.exceptions import APIConnectionError
import litellm
import os
import json
from ion.Utils import count_completion, count_async_completion, setup_logger
import asyncio
import time

litellm._turn_on_debug()

os.environ['LITELLM_LOG'] = 'DEBUG'

completions_logger = setup_logger("completions")

class CompletionQueue:
    def __init__(self, rate_limit=None, tpm_limit=None):
        self.rate_limit = rate_limit
        self.tpm_limit = tpm_limit
        self.queue = asyncio.Queue()
        self.last_request_time = 0
        self.requests_completed = 0
        self.requests_made = 0
        self.last_log_time = 0
        self.max_retries = 5
        self.processing_task = None
        self.tokens_available = tpm_limit
        self.token_lock = asyncio.Lock()
        self.last_tokens_update = time.time()

    def set_rate_limit(self, rate_limit):
        self.rate_limit = rate_limit

    def set_tpm_limit(self, tpm_limit):
        self.tpm_limit = tpm_limit

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
            if not self.rate_limit and not self.tpm_limit:
                raise Exception("Rate limit and TPM limit not set")
            elif not self.rate_limit:
                raise Exception("Rate limit not set")
            elif not self.tpm_limit:
                raise Exception("TPM limit not set")

    
    async def update_tokens_available(self):
        async with self.token_lock:
            current_time = time.time()
            elapsed = current_time - self.last_tokens_update
            tokens_to_add = (elapsed / 60) * self.tpm_limit
            self.tokens_available = min(self.tokens_available + tokens_to_add, self.tpm_limit)
            self.last_tokens_update = current_time
            completions_logger.debug(f"Updated tokens available: {self.tokens_available:.2f}")

    async def process_queue(self):
        while True:
            try:
                # Get the next item from the queue (this will block if queue is empty)
                future, coro_func, args, kwargs, retry_count, estimated_tokens = await self.queue.get()
                
                # Check if we have enough tokens
                process_now = False
                while not process_now:
                    await self.update_tokens_available()
                    
                    async with self.token_lock:
                        if self.tokens_available >= estimated_tokens:
                            self.tokens_available -= estimated_tokens
                            process_now = True
                            completions_logger.info(f"Processing request using {estimated_tokens} tokens. Remaining: {self.tokens_available:.2f}")
                        else:
                            # Calculate how long to wait before checking again
                            tokens_needed = estimated_tokens - self.tokens_available
                            # Calculate time to wait based on token replenishment rate
                            time_to_wait = max(1, (tokens_needed / self.tpm_limit) * 60)
                            completions_logger.info(f"Waiting {time_to_wait:.2f}s for token availability. Need {tokens_needed:.2f} tokens. Available: {self.tokens_available:.2f}")
                            await asyncio.sleep(time_to_wait)
                
                # Now enforce rate limit (requests per second)
                current_time = time.time()
                elapsed = current_time - self.last_request_time
                if elapsed < 1 / self.rate_limit:
                    wait_time = (1 / self.rate_limit) - elapsed
                    completions_logger.debug(f"Rate limiting: waiting {wait_time:.4f}s")
                    await asyncio.sleep(wait_time)
                
                self.last_request_time = time.time()

                # Schedule the request
                asyncio.create_task(self._handle_request(future, coro_func, args, kwargs, retry_count))
                self.queue.task_done()
                self.log_requests()
            except Exception as e:
                completions_logger.error(f"Error in process_queue: {e}", exc_info=True)
                if 'future' in locals() and future and not future.done():
                    future.set_exception(e)
                await asyncio.sleep(1)  # Prevent tight loop in case of persistent errors

    async def _handle_request(self, future, coro_func, args, kwargs, retry_count):
        try:
            if 'o1' in args[0]:
                completions_logger.info("Request is for o1 model")
                # allow reasoning models to take longer
                response = await asyncio.wait_for(coro_func(*args, **kwargs), timeout=300)
            else:
                response = await asyncio.wait_for(coro_func(*args, **kwargs), timeout=60)
            future.set_result(response)
        except asyncio.TimeoutError as e:
            completions_logger.warning("Request timed out")
            if retry_count < self.max_retries:
                self.queue.put_nowait((future, coro_func, args, kwargs, retry_count + 1))
                completions_logger.info(f"Request added back to queue, retry count: {retry_count + 1}")
            else:
                completions_logger.error(f"Request failed after {self.max_retries} retries")
                completions_logger.error(f"Request args: {args}")
                completions_logger.error(f"Request kwargs: {kwargs}")
                future.set_exception(e)
        self.requests_completed += 1

    def log_requests(self):
        current_time = time.time()
        completions_logger.info(f"Requests completed: {self.requests_completed}")
        completions_logger.info(f"Requests made: {self.requests_made}")
        completions_logger.info(f"Tokens available: {self.tokens_available}")
        completions_logger.info(f"Requests in queue: {self.queue.qsize()}")
        if current_time - self.last_log_time >= 1:
            self.requests_completed = 0
            self.requests_made = 0
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
async def generate_async_completion(model, messages, token_limit=None, retry=True, response_format=None):
    input_tokens = token_counter(model=model, messages=messages)
    try:
        if "samba" in model and response_format:
                response_format = { "type": "json_object"}
        if token_limit:
            max_response_tokens = token_limit - input_tokens - 40
            estimated_tokens = input_tokens + max_response_tokens
            response_future = await COMPLETION_QUEUE.add_to_queue(acompletion, model, messages, max_response_tokens, estimated_tokens=estimated_tokens, response_format=response_format)
        else:
            estimated_tokens = input_tokens + 2000
            response_future = await COMPLETION_QUEUE.add_to_queue(acompletion, model, messages, estimated_tokens=estimated_tokens, response_format=response_format)
        response = await response_future
        cost = response._hidden_params["response_cost"]
    except (APIConnectionError, RuntimeError) as e:
        time.sleep(0.5)
        completions_logger.warning("APIConnectionError: Retrying...")
        if retry:
            if "samba" in model and response_format:
                response_format = { "type": "json_object"}
            response = await generate_async_completion(model, messages, token_limit, retry=False, response_format=response_format)
        else:
            raise e
        cost = 0
        completion_result = {"model": model, "cost": cost, "response": response}
        return completion_result
    completion_result = {"model": model, "cost": cost, "response": response.choices[0].message.content}
    return completion_result







