"""Baseline attack registry and lightweight renderers."""

from .registry import BASELINES, baseline_metadata, render_registered_baseline

__all__ = ["BASELINES", "baseline_metadata", "render_registered_baseline"]
