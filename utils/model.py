import uuid
from openai import OpenAI, APIError
import re
import os
from utils.config import read_config

config = read_config(os.path.join(os.path.dirname(__file__), '..', 'Attack', 'config.json'))

BASE_URLS = {
    "deepseek": "https://api.deepseek.com",
    "gpt": "https://xiaoai.plus/v1",
    "o1": "https://api.openai.com/v1",
    "o3": "https://xiaoai.plus/v1",
    "qwq": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "llama": "https://openrouter.ai/api/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "gemini":"https://xiaoai.plus/v1"
}

def split_think_content(text):
    pattern = r"<think>(.*?)</think>(.*)"
    match = re.match(pattern, text, re.DOTALL)
    if match:
        think_content = match.group(1).strip()
        rest_content = match.group(2).strip()
        return think_content, rest_content
    else:
        return None, text.strip()
    

def _openai_chat_stream(
    input_prompt, api_key,
    logger, debug_logger,   
    base_url, model_type, temperature, max_tokens
):
    assert isinstance(input_prompt, str), "OpenAI API does not support batch inference."
    client = OpenAI(api_key=api_key, base_url=base_url)
    logger.info(f"Sending message: {input_prompt} to model: {model_type}")
    
    messages = [{"role": "user", "content": input_prompt}]
    response, reason = "", ""
    is_answering = False

    try:
        completion = client.chat.completions.create(
            model=model_type,
            extra_body={"enable_thinking":True},
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        for chunk in completion:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if delta is None:
                continue
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                reason += str(delta.reasoning_content)
            else:
                if delta.content and not is_answering:
                    is_answering = True
                if delta.content:  
                    response += str(delta.content)

    except APIError as e:
        err = str(e)
        if "Output data may contain inappropriate content." in err:
            logger.warning("⚠️ Output data may contain inappropriate content")
        else:
            logger.error(f"❌ OpenAI API Error: {err}")


    # === Clean up None at the beginning of response ===
    if response.startswith("None"):
        response = response[len("None"):].lstrip()
    # Alternatively, use regex for more safety:
    # response = re.sub(r"^None\s*", "", response)

    # === Logging optimization section ===
    log_id = str(uuid.uuid4())[:8]  # Short ID
    short_response = response[:15] + ("..." if len(response) > 10 else "")
    short_reason = reason[:15] + ("..." if len(reason) > 10 else "")

    logger.info(f"[{log_id}] Response: {short_response}; Reason: {short_reason} (see debug log)")
    debug_logger.debug(f"[{log_id}] FULL Response: {response}")
    debug_logger.debug(f"[{log_id}] FULL Reason: {reason}")
    # ===================

    if "claude" in model_type:
        reason, response = split_think_content(response)

    return response, reason


def Generate(input_prompt, model_type, temperature, max_tokens, api_key, logger, debug_logger):
    base_url = None

    # First, look up in BASE_URLS
    for key in BASE_URLS:
        if key in model_type:
            base_url = BASE_URLS[key]
            break

    # If not found, try to find model name + '_url' in config
    if not base_url:
        config_key = model_type + '_url'
        base_url = config.get(config_key)

    if not base_url:
        raise ValueError(f"Unsupported model_type: {model_type}, and no URL found in config for key '{config_key}'")

    return _openai_chat_stream(
        input_prompt=input_prompt,
        api_key=api_key,
        logger=logger,
        debug_logger=debug_logger,
        base_url=base_url,
        model_type=model_type,
        temperature=temperature,
        max_tokens=max_tokens
    )
