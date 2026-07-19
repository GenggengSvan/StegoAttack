import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_path(*parts: Union[str, os.PathLike]) -> Path:
    """Return a path under the repository root."""
    return PROJECT_ROOT.joinpath(*map(Path, parts)) if parts else PROJECT_ROOT


def resolve_path(path_value: Union[str, os.PathLike], base_dir: Optional[Union[str, os.PathLike]] = None) -> Path:
    """Resolve a config path relative to a config directory, then the repo root."""
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    if base_dir is not None:
        candidate = Path(base_dir).expanduser() / path
        if candidate.exists():
            return candidate.resolve()
    return (PROJECT_ROOT / path).resolve()


def read_config(config_path: Optional[Union[str, os.PathLike]] = None) -> Dict[str, Any]:
    """Read a JSON configuration file.

    When no path is supplied, prefer the current directory's config.json and
    then fall back to Attack/config.json for backward compatibility.
    """
    if config_path is None:
        cwd_config = Path.cwd() / "config.json"
        config_path = cwd_config if cwd_config.exists() else PROJECT_ROOT / "Attack" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_llm_env(config: Dict[str, Any], model_key: str = "model_type", api_key: str = "api_key") -> Dict[str, Any]:
    """Overlay standard LLM_* environment variables onto a config copy."""
    merged = dict(config)
    env_model = os.environ.get("LLM_MODEL")
    env_api_key = os.environ.get("LLM_API_KEY")
    env_base_url = os.environ.get("LLM_BASE_URL")
    if env_model:
        merged[model_key] = env_model
    if env_api_key:
        merged[api_key] = env_api_key
    if env_base_url:
        merged["base_url"] = env_base_url
    return merged


def redacted(value: Optional[str]) -> str:
    """Return a non-secret representation for logs and JSON diagnostics."""
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}...{value[-4:]}"
