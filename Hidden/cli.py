"""Command-line interface for the Hidden text-hiding stage."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from .text_hider import (
        DEFAULT_VOCAB,
        HiddenRunConfig,
        SUPPORTED_METHODS,
        build_masked_text,
        default_output_path,
        generate_hidden_sentence,
        hide_many_texts,
        hide_single_text,
        load_input_records,
        load_vocab,
        parse_position,
        tokenize_query,
        write_records,
    )
except ImportError:
    from text_hider import (
        DEFAULT_VOCAB,
        HiddenRunConfig,
        SUPPORTED_METHODS,
        build_masked_text,
        default_output_path,
        generate_hidden_sentence,
        hide_many_texts,
        hide_single_text,
        load_input_records,
        load_vocab,
        parse_position,
        tokenize_query,
        write_records,
    )

from utils.config import resolve_path


def _run_config_from_args(
    method: str,
    position_str: str,
    sentence_length: int,
    vocab_path: Optional[Path],
    dry_run: bool,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    seed: Optional[int] = None,
) -> HiddenRunConfig:
    return HiddenRunConfig(
        method=method,
        position=position_str,
        sentence_length=sentence_length,
        vocab_path=vocab_path,
        dry_run=dry_run,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed,
    )


def process_text(
    text: str,
    method: str = "masked",
    position_str: str = "first",
    output_path: Optional[Path] = None,
    sentence_length: int = 10,
    vocab_path: Optional[Path] = None,
    dry_run: bool = False,
    json_summary: bool = False,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    seed: Optional[int] = None,
):
    """Hide one input text and optionally save it as a one-record JSON file."""
    run_config = _run_config_from_args(
        method,
        position_str,
        sentence_length,
        vocab_path,
        dry_run,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed,
    )
    record = hide_single_text(text, run_config=run_config, input_key="query", console_logs=not json_summary)
    if output_path:
        write_records([record], output_path)

    if json_summary:
        print(json.dumps(record, ensure_ascii=False, indent=2))
    else:
        print("Hidden output:")
        print(record["answer_hidden"])
        if record.get("requires_model"):
            print("\nRegenerated hidden text:")
            print(record["answer_hidden_response"])
        if output_path:
            print(f"\nResult saved to: {resolve_path(output_path)}")
    return record


def process_pipeline(
    input_path: Path,
    input_key: str,
    method: str = "masked",
    position_str: str = "first",
    output_path: Optional[Path] = None,
    sentence_length: int = 10,
    vocab_path: Optional[Path] = None,
    limit: Optional[int] = None,
    dry_run: bool = False,
    json_summary: bool = False,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    seed: Optional[int] = None,
) -> Path:
    """Process a CSV/JSON file and write Hidden-stage records."""
    emit = (lambda *args, **kwargs: None) if json_summary else print
    input_path = resolve_path(input_path)
    emit("Step 1: Loading input records...")
    queries = load_input_records(input_path, input_key)
    if limit is not None:
        queries = queries[:limit]

    emit("Step 2: Hiding input words...")
    run_config = _run_config_from_args(
        method,
        position_str,
        sentence_length,
        vocab_path,
        dry_run,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed,
    )
    results = hide_many_texts(queries, run_config=run_config, input_key=input_key, console_logs=not json_summary)

    emit("Step 3: Saving results...")
    if output_path is None:
        output_path = default_output_path(input_path.stem, position_str, method)
    write_records(results, output_path)

    summary = {
        "output_path": str(resolve_path(output_path)),
        "total_samples": len(results),
        "position": position_str,
        "method": method,
        "dry_run": dry_run or method != "masked",
        "requires_model": method == "masked" and not dry_run,
        "model": model,
    }
    if json_summary:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("\nProcessing finished successfully!")
        print(f"Results saved to: {resolve_path(output_path)}")
    return resolve_path(output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hide one text or a CSV/JSON batch using masked regeneration or encodings.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="One piece of text to hide.")
    source.add_argument("--input", type=Path, help="Path to input CSV or JSON file.")
    parser.add_argument("--key", type=str, default="query", help="CSV/JSON key containing input text.")
    parser.add_argument("--method", choices=SUPPORTED_METHODS, default="masked", help="Hiding method.")
    parser.add_argument("--position", type=str, default="first", help="Hidden word position, e.g. first, second, last, -1.")
    parser.add_argument("--output", type=Path, help="Optional output JSON path.")
    parser.add_argument("--len", "--length", dest="length", type=int, default=10, help="Carrier sentence length.")
    parser.add_argument("--vocab", type=Path, help="Optional custom vocabulary file.")
    parser.add_argument("--limit", type=int, help="Limit number of input rows for file mode.")
    parser.add_argument("--dry-run", action="store_true", help="Generate the masked skeleton only; do not call an LLM.")
    parser.add_argument("--model", help="Model name, e.g. deepseek-v4-pro.")
    parser.add_argument("--api-key", help="API key. Prefer LLM_API_KEY for shell history hygiene.")
    parser.add_argument("--base-url", help="OpenAI-compatible API base URL.")
    parser.add_argument("--temperature", type=float, help="Generation temperature.")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens for regeneration.")
    parser.add_argument("--seed", type=int, help="Deterministic filler-word seed.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.text is not None:
            process_text(
                text=args.text,
                method=args.method,
                position_str=args.position,
                output_path=args.output,
                sentence_length=args.length,
                vocab_path=args.vocab,
                dry_run=args.dry_run,
                json_summary=args.json,
                model=args.model,
                api_key=args.api_key,
                base_url=args.base_url,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                seed=args.seed,
            )
        else:
            process_pipeline(
                input_path=args.input,
                input_key=args.key,
                method=args.method,
                position_str=args.position,
                output_path=args.output,
                sentence_length=args.length,
                vocab_path=args.vocab,
                limit=args.limit,
                dry_run=args.dry_run,
                json_summary=args.json,
                model=args.model,
                api_key=args.api_key,
                base_url=args.base_url,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                seed=args.seed,
            )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
