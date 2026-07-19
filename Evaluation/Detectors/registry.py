"""References for external safety detectors.

This file intentionally does not implement detector inference. It records model
links and suggested external serving commands only.
"""

from typing import Dict


DETECTOR_REFERENCES: Dict[str, Dict[str, str]] = {
    "llamaguard": {
        "name": "Meta Llama Guard",
        "model_id": "meta-llama/Llama-Guard-3-8B",
        "download_url": "https://huggingface.co/meta-llama/Llama-Guard-3-8B",
        "serve_example": "vllm serve meta-llama/Llama-Guard-3-8B",
    },
    "shieldlm": {
        "name": "ShieldLM",
        "model_id": "thu-coai/ShieldLM-7B-internlm2",
        "download_url": "https://huggingface.co/thu-coai/ShieldLM-7B-internlm2",
        "serve_example": "vllm serve thu-coai/ShieldLM-7B-internlm2 --trust-remote-code",
    },
    "wildguard": {
        "name": "WildGuard",
        "model_id": "allenai/wildguard",
        "download_url": "https://huggingface.co/allenai/wildguard",
        "serve_example": "vllm serve allenai/wildguard",
    },
}


def detector_references() -> Dict[str, Dict[str, str]]:
    return DETECTOR_REFERENCES
