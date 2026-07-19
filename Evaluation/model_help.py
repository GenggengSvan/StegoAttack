"""Model download and invocation guidance for Evaluation components."""

import json
from typing import Dict


MODEL_HELP: Dict[str, Dict] = {
    "ppl-gpt2": {
        "name": "GPT-2 for perplexity",
        "download_url": "https://huggingface.co/openai-community/gpt2",
        "model_id": "openai-community/gpt2",
        "used_by": "Evaluation/PPL/PPL_Text.py",
        "local_call": [
            "from transformers import GPT2TokenizerFast, GPT2LMHeadModel",
            "tokenizer = GPT2TokenizerFast.from_pretrained('openai-community/gpt2')",
            "model = GPT2LMHeadModel.from_pretrained('openai-community/gpt2')",
        ],
        "repo_call": (
            "Set Evaluation/PPL/config.json model_path to 'openai-community/gpt2' "
            "or to a local Hugging Face snapshot path, then run: "
            "python3 Evaluation/PPL/PPL_Text.py"
        ),
    },
    "llamaguard": {
        "name": "Meta Llama Guard",
        "download_url": "https://huggingface.co/meta-llama/Llama-Guard-3-8B",
        "model_id": "meta-llama/Llama-Guard-3-8B",
        "used_by": "External detector workflow; not integrated locally.",
        "local_call": [
            "vllm serve meta-llama/Llama-Guard-3-8B",
            "Run the detector with its upstream prompt/API, export a summary JSON, "
            "then pass that summary to stego_cli.py guard-reduction.",
        ],
        "repo_call": "No local guard adapter is shipped in this repository.",
    },
    "shieldlm": {
        "name": "ShieldLM",
        "download_url": "https://huggingface.co/thu-coai/ShieldLM-7B-internlm2",
        "model_id": "thu-coai/ShieldLM-7B-internlm2",
        "used_by": "External detector workflow; not integrated locally.",
        "local_call": [
            "vllm serve thu-coai/ShieldLM-7B-internlm2 --trust-remote-code",
            "Run the detector with its upstream prompt/API, export a summary JSON, "
            "then pass that summary to stego_cli.py guard-reduction.",
        ],
        "repo_call": "No local guard adapter is shipped in this repository.",
    },
    "wildguard": {
        "name": "WildGuard",
        "download_url": "https://huggingface.co/allenai/wildguard",
        "model_id": "allenai/wildguard",
        "used_by": "External detector workflow; not integrated locally.",
        "local_call": [
            "vllm serve allenai/wildguard",
            "Run the detector with its upstream prompt/API, export a summary JSON, "
            "then pass that summary to stego_cli.py guard-reduction.",
        ],
        "repo_call": "No local guard adapter is shipped in this repository.",
    },
}


def evaluation_model_help() -> Dict:
    return {
        "models": MODEL_HELP,
        "notes": [
            "ASR does not require a model; it reads existing JSON analysis fields.",
            "Grammar uses language_tool_python and may download/start a LanguageTool backend; no Hugging Face model is required.",
            "Guard detectors are not integrated locally.",
            "Use external detector outputs with stego_cli.py guard-reduction.",
        ],
    }


def format_model_help() -> str:
    lines = ["Evaluation model help:"]
    for key, item in MODEL_HELP.items():
        lines.append(f"- {key}: {item['name']}")
        lines.append(f"  Download: {item['download_url']}")
        lines.append(f"  Model id: {item['model_id']}")
        lines.append(f"  Used by: {item['used_by']}")
        lines.append(f"  Call: {item['repo_call']}")
    return "\n".join(lines)


def model_help_json() -> str:
    return json.dumps(evaluation_model_help(), ensure_ascii=False, indent=2)
