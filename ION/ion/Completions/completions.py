from litellm import Router
from litellm.exceptions import APIConnectionError
from ion.Utils import count_completion, count_async_completion, setup_logger


completions_logger = setup_logger("completions")


ROUTER = {}

def get_router(model_list):
    global ROUTER
    if ROUTER == {}:
        ROUTER = Router(model_list)
        completions_logger.info(f"Router created with models: {model_list}")
    else:
        completions_logger.info("Router already initialized")


# regular completion
@count_completion
def generate_completion(model, messages, response_format=None, tools=None, full_message=False):
    try:
        kwargs = {}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if response_format:
            if "samba" in model:
                response_format = { "type": "json_object"}
            else:
                kwargs["response_format"] = response_format
        response = ROUTER.completion(model=model, messages=messages, **kwargs)
        cost = response._hidden_params["response_cost"]
    except (APIConnectionError, RuntimeError) as e:
        raise e
    if full_message:
        completion_result = {"model": model, "cost": cost, "response": response.choices[0].message}
    else:
        completion_result = {"model": model, "cost": cost, "response": response.choices[0].message.content}
    return completion_result


#async completion
@count_async_completion
async def generate_async_completion(model, messages, response_format=None, tools=None, full_message=False):
    try:
        kwargs = {}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if response_format:
            if "samba" in model:
                response_format = { "type": "json_object"}
            else:
                kwargs["response_format"] = response_format
        response = await ROUTER.acompletion(model, messages, **kwargs)
        cost = response._hidden_params["response_cost"]
    except (APIConnectionError, RuntimeError) as e:
        raise e
    if full_message:
        completion_result = {"model": model, "cost": cost, "response": response.choices[0].message}
    else:
        completion_result = {"model": model, "cost": cost, "response": response.choices[0].message.content}
    return completion_result







