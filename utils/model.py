import os
import re
import uuid

from openai import APIError, OpenAI

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


def resolve_model_settings(model_type=None, api_key=None, base_url=None):
    """Resolve model settings from arguments, environment, config, and defaults."""
    env_model = os.environ.get("LLM_MODEL")
    if not model_type or model_type == "[MODEL]":
        model_type = env_model
    api_key = api_key if api_key and api_key != "[API_KEY]" else os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL") or base_url

    if not model_type:
        model_type = config.get("attack_target_model_type") or config.get("model_type")
    if not api_key:
        api_key = config.get("attack_target_api_key") or config.get("api_key")

    derived_base_url = False
    if not base_url and model_type:
        for key, url in BASE_URLS.items():
            if key in model_type:
                base_url = url
                derived_base_url = True
                break

    if not base_url and model_type:
        base_url = config.get(f"{model_type}_url")

    if not base_url:
        raise ValueError(f"Unsupported model_type: {model_type!r}; set LLM_BASE_URL or add '<model>_url' to config.")
    if not api_key or api_key == "[API_KEY]":
        raise ValueError("Missing API key. Set LLM_API_KEY or the relevant config api key.")

    # DeepSeek's direct API expects names such as deepseek-v4-pro. Keep provider
    # prefixes for OpenRouter or other explicitly supplied non-DeepSeek URLs.
    if "api.deepseek.com" in base_url and model_type.startswith("deepseek/"):
        model_type = model_type.split("/", 1)[1]

    return model_type, api_key, base_url

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
        kwargs = {
            "model": model_type,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if any(name in model_type for name in ("deepseek", "qwen", "qwq")):
            kwargs["extra_body"] = {"enable_thinking": True}
        completion = client.chat.completions.create(**kwargs)

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
        raise RuntimeError(f"LLM API call failed for model {model_type}: {err}") from e


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


def Generate(input_prompt, model_type, temperature, max_tokens, api_key, logger, debug_logger, base_url=None):
    model_type, api_key, base_url = resolve_model_settings(model_type, api_key, base_url)
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
