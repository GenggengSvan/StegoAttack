from openai import OpenAI, APIError
import re

BASE_URLS = {
    "deepseek": "https://api.deepseek.com",
    "gpt": "https://api.openai.com/v1",
    "o1": "https://api.openai.com/v1",
    "o3": "https://api.openai.com/v1",
    "qwq": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "Llama": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
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
    
def _openai_chat_stream(input_prompt, api_key, logger, base_url, model_type, temperature, max_tokens):
    assert isinstance(input_prompt, str), "OpenAI API does not support batch inference."
    client = OpenAI(api_key=api_key, base_url=base_url)
    logger.info(f"Sending message: {input_prompt} to model: {model_type}")
    
    messages = [{"role": "user", "content": input_prompt}]
    response, reason = "", ""
    is_answering = False

    try:
        completion = client.chat.completions.create(
            model=model_type,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        for chunk in completion:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                print(delta.reasoning_content, end='', flush=True)
                reason += str(delta.reasoning_content)
            else:
                if delta.content and not is_answering:
                    print("\n" + "=" * 20 + " Full Response " + "=" * 20 + "\n")
                    is_answering = True
                print(delta.content, end='', flush=True)
                if delta.content != "None":
                    response += str(delta.content)

    except APIError as e:
        err = str(e)
        if "Output data may contain inappropriate content." in err:
            print("\n⚠️ Output data may contain inappropriate content")
        else:
            print(f"\n❌ OpenAI API Error: {err}")

    logger.info(f"Response: {response};\n Reason: {reason}")

    if "claude" in model_type:
        reason,response = split_think_content(response)

    return response, reason


def Generate(input_prompt, model_type, temperature, max_tokens, api_key, logger):
    base_url = None
    for key in BASE_URLS:
        if key in model_type:
            base_url = BASE_URLS[key]
            break

    if not base_url:
        raise ValueError(f"Unsupported model_type: {model_type}")
    return _openai_chat_stream(
        input_prompt=input_prompt,
        api_key=api_key,
        logger=logger,
        base_url=base_url,
        model_type=model_type,
        temperature=temperature,
        max_tokens=max_tokens
    )
