"""Hidden text generation package."""

from .text_hider import SUPPORTED_METHODS, HiddenRunConfig, build_masked_text, hide_many_texts, hide_single_text

__all__ = [
    "SUPPORTED_METHODS",
    "HiddenRunConfig",
    "build_masked_text",
    "hide_many_texts",
    "hide_single_text",
]
