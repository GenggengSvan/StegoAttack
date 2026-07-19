"""Shared baseline metadata and rendering helpers."""

from dataclasses import asdict, dataclass
from importlib import import_module
from typing import Dict, Optional


@dataclass(frozen=True)
class BaselineSpec:
    name: str
    display_name: str
    family: str
    paper_title: str
    paper_reference: str
    venue: str = ""
    paper_url: str = ""
    code_url: str = ""
    description: str = ""
    implementation_status: str = "documented"
    renderer_module: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


def render_baseline(spec: BaselineSpec, query: str, **kwargs) -> Dict:
    """Render a baseline prompt when migrated upstream prompt code is available."""
    if spec.renderer_module:
        module = import_module(spec.renderer_module)
        rendered = module.render(query=query, **kwargs)
        rendered.setdefault("baseline", spec.name)
        rendered.setdefault("display_name", spec.display_name)
        rendered.setdefault("implementation_status", spec.implementation_status)
        rendered.setdefault("paper_reference", spec.paper_reference)
        return rendered

    return {
        "baseline": spec.name,
        "display_name": spec.display_name,
        "family": spec.family,
        "paper_reference": spec.paper_reference,
        "implementation_status": spec.implementation_status,
        "input_query": query,
        "prompt": None,
        "reason": (
            "This baseline is documented in Baselines, but no migrated prompt "
            "renderer is shipped. Use the linked paper/code for full reproduction."
        ),
    }
