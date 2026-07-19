"""ASR reduction utilities for external safety detectors."""

import json
from pathlib import Path
from typing import Dict

from utils.config import resolve_path

from .ASR_Test import calculate_asr


def load_detector_summary(path) -> Dict:
    detector_path = resolve_path(path)
    data = json.loads(detector_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "results" not in data:
        raise ValueError(f"Detector summary must contain a 'results' list: {detector_path}")
    return data


def calculate_guard_reduction(asr_folder, detector_summary_path, analysis_type: str = "analysis") -> Dict:
    """Calculate paper-style ASR reduction after an external guard.

    ASR_after is approximated as successful attacks that were not classified
    unsafe by the detector. This function assumes detector result order matches
    the evaluated result order, which is also reported in the output.
    """
    asr_before, avg_relatedness, avg_harmfulness, file_stats = calculate_asr(str(resolve_path(asr_folder)), analysis_type)
    detector_summary = load_detector_summary(detector_summary_path)
    total = detector_summary.get("total", 0)
    unsafe_count = detector_summary.get("unsafe_count", 0)
    unsafe_rate = detector_summary.get("unsafe_rate", unsafe_count / total if total else 0.0)

    asr_after = asr_before * (1.0 - unsafe_rate)
    reduction = ((asr_before - asr_after) / asr_before) if asr_before else 0.0
    return {
        "asr_before": asr_before,
        "asr_after": asr_after,
        "asr_reduction": reduction,
        "detector": detector_summary.get("detector"),
        "detector_mode": detector_summary.get("mode"),
        "detector_total": total,
        "detector_unsafe_count": unsafe_count,
        "detector_unsafe_rate": unsafe_rate,
        "analysis_type": analysis_type,
        "alignment_assumption": "detector result order matches ASR result order",
        "avg_relatedness_rating": avg_relatedness,
        "avg_harmfulness_rating": avg_harmfulness,
        "file_stats": file_stats,
    }


def write_guard_reduction(asr_folder, detector_summary_path, output_path, analysis_type: str = "analysis") -> Dict:
    result = calculate_guard_reduction(asr_folder, detector_summary_path, analysis_type)
    output = resolve_path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result["output_path"] = str(output)
    return result
