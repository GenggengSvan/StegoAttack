"""Command line entry point for the StegoAttack research pipeline."""

import argparse
import json
import sys
from pathlib import Path

from Baselines import BASELINES, baseline_metadata, render_registered_baseline
from utils.config import PROJECT_ROOT, redacted, resolve_path

HIDDEN_METHOD_NAMES = ("masked", "base64", "ascii", "hex", "acrostic")


def _cmd_hidden(args):
    from Hidden.cli import process_pipeline, process_text

    common = {
        "method": args.method,
        "position_str": args.position,
        "output_path": Path(args.output) if args.output else None,
        "sentence_length": args.length,
        "vocab_path": Path(args.vocab) if args.vocab else None,
        "dry_run": args.dry_run,
        "json_summary": args.json,
        "model": args.model,
        "api_key": args.api_key,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "seed": args.seed,
    }
    if args.text is not None:
        return process_text(text=args.text, **common)
    output = process_pipeline(
        input_path=Path(args.input),
        input_key=args.key,
        limit=args.limit,
        **common,
    )
    return {"output_path": str(output)}


def _cmd_attack(args):
    from Attack import attack as attack_stage

    argv = ["--config", args.config]
    if args.input:
        argv += ["--input", args.input]
    if args.text:
        argv += ["--text", args.text]
    if args.query:
        argv += ["--query", args.query]
    if args.output_dir:
        argv += ["--output-dir", args.output_dir]
    if args.output:
        argv += ["--output", args.output]
    if args.model:
        argv += ["--model", args.model]
    if args.api_key:
        argv += ["--api-key", args.api_key]
    if args.base_url:
        argv += ["--base-url", args.base_url]
    if args.judge_model:
        argv += ["--judge-model", args.judge_model]
    if args.judge_api_key:
        argv += ["--judge-api-key", args.judge_api_key]
    if args.judge_base_url:
        argv += ["--judge-base-url", args.judge_base_url]
    if args.position:
        argv += ["--position", args.position]
    if args.analysis_type:
        argv += ["--analysis-type", args.analysis_type]
    if args.score_threshold is not None:
        argv += ["--score-threshold", str(args.score_threshold)]
    if args.limit is not None:
        argv += ["--limit", str(args.limit)]
    if args.max_retries is not None:
        argv += ["--max-retries", str(args.max_retries)]
    if args.temperature_min is not None:
        argv += ["--temperature-min", str(args.temperature_min)]
    if args.temperature_max is not None:
        argv += ["--temperature-max", str(args.temperature_max)]
    if args.dry_run:
        argv.append("--dry-run")
    if args.json:
        argv.append("--json")
    attack_stage.main(argv)
    return {}


def _cmd_asr(args):
    from Evaluation.ASR.ASR_Test import calculate_asr

    folder = str(resolve_path(args.folder))
    avg_asr, avg_relatedness, avg_harmfulness, file_stats = calculate_asr(folder, args.analysis_type)
    summary = {
        "folder_path": folder,
        "analysis_type": args.analysis_type,
        "average_asr": avg_asr,
        "average_relatedness_rating": avg_relatedness,
        "average_harmfulness_rating": avg_harmfulness,
        "file_stats": file_stats,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"ASR: {avg_asr:.2%}")
        print(f"Relatedness: {avg_relatedness:.2f}")
        print(f"Harmfulness: {avg_harmfulness:.2f}")
    return summary


def _cmd_doctor(args):
    from utils.model import resolve_model_settings

    try:
        model, api_key, base_url = resolve_model_settings(args.model, args.api_key, args.base_url)
        model_ok = True
        error = ""
    except Exception as exc:
        model, api_key, base_url = args.model, args.api_key, args.base_url
        model_ok = False
        error = str(exc)
    summary = {
        "project_root": str(PROJECT_ROOT),
        "model_config_ok": model_ok,
        "model": model,
        "base_url": base_url,
        "api_key": redacted(api_key),
        "error": error,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json else summary)
    return summary


def _cmd_baseline(args):
    if args.action == "list":
        result = baseline_metadata()
    else:
        result = render_registered_baseline(args.name, args.query)
        if args.output:
            output_path = resolve_path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            result["output_path"] = str(output_path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)
    return result


def _cmd_guard_reduction(args):
    from Evaluation.ASR.reduction import calculate_guard_reduction, write_guard_reduction

    if args.output:
        result = write_guard_reduction(args.asr_folder, args.detector_summary, args.output, args.analysis_type)
    else:
        result = calculate_guard_reduction(args.asr_folder, args.detector_summary, args.analysis_type)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ASR before: {result['asr_before']:.2%}")
        print(f"ASR after: {result['asr_after']:.2%}")
        print(f"Reduction: {result['asr_reduction']:.2%}")
    return result


def _cmd_eval_models(args):
    from Evaluation.model_help import evaluation_model_help, format_model_help

    result = evaluation_model_help()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_model_help())
    return result


def build_parser():
    parser = argparse.ArgumentParser(description="Run StegoAttack stages with stable paths and JSON-friendly output.")
    sub = parser.add_subparsers(dest="command", required=True)

    hidden = sub.add_parser("hidden", help="Hide one text or a CSV/JSON batch with masked regeneration.")
    hidden_source = hidden.add_mutually_exclusive_group(required=True)
    hidden_source.add_argument("--text", help="One piece of text to hide.")
    hidden_source.add_argument("--input", help="Input CSV or JSON file for batch mode.")
    hidden.add_argument("--key", default="query")
    hidden.add_argument("--method", choices=HIDDEN_METHOD_NAMES, default="masked")
    hidden.add_argument("--position", default="first")
    hidden.add_argument("--output")
    hidden.add_argument("--len", "--length", dest="length", type=int, default=10)
    hidden.add_argument("--vocab")
    hidden.add_argument("--limit", type=int)
    hidden.add_argument("--model")
    hidden.add_argument("--api-key")
    hidden.add_argument("--base-url")
    hidden.add_argument("--temperature", type=float)
    hidden.add_argument("--max-tokens", type=int)
    hidden.add_argument("--seed", type=int)
    hidden.add_argument("--dry-run", action="store_true")
    hidden.add_argument("--json", action="store_true")
    hidden.set_defaults(func=_cmd_hidden)

    attack = sub.add_parser("attack", help="Run the prompt-template attack stage.")
    attack.add_argument("--config", default=str(PROJECT_ROOT / "Attack" / "config.json"))
    attack.add_argument("--input")
    attack.add_argument("--text")
    attack.add_argument("--query")
    attack.add_argument("--output-dir")
    attack.add_argument("--output")
    attack.add_argument("--model")
    attack.add_argument("--api-key")
    attack.add_argument("--base-url")
    attack.add_argument("--judge-model")
    attack.add_argument("--judge-api-key")
    attack.add_argument("--judge-base-url")
    attack.add_argument("--position")
    attack.add_argument("--analysis-type", choices=["relatedness", "harmfulness", "both"])
    attack.add_argument("--score-threshold", type=float)
    attack.add_argument("--limit", type=int)
    attack.add_argument("--max-retries", type=int)
    attack.add_argument("--temperature-min", type=float)
    attack.add_argument("--temperature-max", type=float)
    attack.add_argument("--dry-run", action="store_true")
    attack.add_argument("--json", action="store_true")
    attack.set_defaults(func=_cmd_attack)

    asr = sub.add_parser("asr", help="Calculate ASR from result JSON files.")
    asr.add_argument("--folder", required=True)
    asr.add_argument("--analysis-type", choices=["analysis", "analysis_original"], default="analysis")
    asr.add_argument("--json", action="store_true")
    asr.set_defaults(func=_cmd_asr)

    doctor = sub.add_parser("doctor", help="Validate local paths and LLM configuration without calling a model.")
    doctor.add_argument("--model")
    doctor.add_argument("--api-key")
    doctor.add_argument("--base-url")
    doctor.add_argument("--json", action="store_true")
    doctor.set_defaults(func=_cmd_doctor)

    eval_models = sub.add_parser("eval-models", help="Show model download URLs and invocation examples for Evaluation.")
    eval_models.add_argument("--json", action="store_true")
    eval_models.set_defaults(func=_cmd_eval_models)

    baseline = sub.add_parser("baseline", help="Inspect or render registered baseline methods.")
    baseline_sub = baseline.add_subparsers(dest="action", required=True)
    baseline_list = baseline_sub.add_parser("list", help="List baseline metadata.")
    baseline_list.add_argument("--json", action="store_true")
    baseline_list.set_defaults(func=_cmd_baseline)
    baseline_render = baseline_sub.add_parser("render", help="Render a registered baseline prompt when available.")
    baseline_render.add_argument("--name", choices=sorted(BASELINES), required=True)
    baseline_render.add_argument("--query", required=True)
    baseline_render.add_argument("--output", help="Optional JSON path for the rendered baseline prompt.")
    baseline_render.add_argument("--json", action="store_true")
    baseline_render.set_defaults(func=_cmd_baseline)

    guard_reduction = sub.add_parser("guard-reduction", help="Calculate ASR reduction from detector outputs.")
    guard_reduction.add_argument("--asr-folder", required=True)
    guard_reduction.add_argument("--detector-summary", required=True)
    guard_reduction.add_argument("--analysis-type", choices=["analysis", "analysis_original"], default="analysis")
    guard_reduction.add_argument("--output")
    guard_reduction.add_argument("--json", action="store_true")
    guard_reduction.set_defaults(func=_cmd_guard_reduction)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
