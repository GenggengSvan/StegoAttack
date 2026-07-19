# Hidden

> Hide any text as a carrier paragraph or a reversible encoded payload.

## ⚡ One-Liner

```bash
python3 stego_cli.py hidden \
  --text "Plan a city garden schedule" \
  --method masked \
  --position second \
  --dry-run \
  --json
```

For LLM regeneration:

```bash
export LLM_API_KEY="your-api-key"

python3 stego_cli.py hidden \
  --text "Plan a city garden schedule" \
  --method masked \
  --position second \
  --model deepseek-v4-pro \
  --base-url https://api.deepseek.com/v1 \
  --json
```

## 🧭 Methods

| Method | What It Does | Model Needed |
| --- | --- | --- |
| `masked` | Paper-style masked regeneration. Each input word is placed at a chosen word position, then optionally rewritten by an LLM. | Optional |
| `base64` | Encodes the UTF-8 input as Base64. | No |
| `ascii` | Emits decimal character code points. ASCII text stays plain ASCII codes. | No |
| `hex` | Encodes UTF-8 bytes as hexadecimal. | No |
| `acrostic` | Writes one line per hex character; the first characters spell the hidden payload. | No |

Examples:

```bash
python3 stego_cli.py hidden --text "Garden 42" --method base64 --json
python3 stego_cli.py hidden --text "Garden 42" --method ascii --json
python3 stego_cli.py hidden --text "Garden 42" --method hex --json
python3 stego_cli.py hidden --text "Garden 42" --method acrostic --json
```

## 🎛️ Key Options

- `--text`: hide one piece of text.
- `--input` + `--key`: hide a CSV/JSON batch.
- `--method`: `masked`, `base64`, `ascii`, `hex`, or `acrostic`.
- `--position`: for `masked`; examples: `first`, `second`, `last`, `-1`.
- `--len`: carrier sentence length for `masked`.
- `--seed`: reproducible filler words for `masked`.
- `--dry-run`: skip LLM regeneration.
- `--model`, `--base-url`, `--api-key`: OpenAI-compatible model settings.
- `--output`: save JSON output.

Prefer `LLM_API_KEY` over `--api-key` so secrets do not land in shell history.

## 📦 Batch Mode

```bash
python3 stego_cli.py hidden \
  --input Data/Advbench-50/harmful_behaviors.csv \
  --key query \
  --method masked \
  --position second \
  --limit 5 \
  --dry-run \
  --json
```

Input JSON may be a list of strings, a list of objects, or an object whose
`--key` value is a string/list.

## 🧩 Python API

```python
from Hidden.text_hider import HiddenRunConfig, hide_single_text

record = hide_single_text(
    "Plan a city garden schedule",
    HiddenRunConfig(method="masked", position="second", dry_run=True, seed=7),
)

print(record["answer_hidden_response"])
```

## 🗂️ Files

- `text_hider.py`: core hiding methods.
- `cli.py`: Hidden command-line interface.
- `analysis.py`: response/refusal and word-alignment helpers.
- `config.json`: default model and runtime settings.

## 🔭 Future Work

- `zero_width`: hide bits with zero-width Unicode characters such as ZWSP/ZWNJ.
  This is compact and visually stealthy, but it needs careful decode tooling,
  copy/paste tests, and explicit inspection warnings before becoming a default
  method.
- Add decode commands for every reversible method: `base64`, `ascii`, `hex`,
  `acrostic`, and future `zero_width`.
- Add richer carrier templates for `acrostic`, so the output reads less like a
  mechanical placeholder.

## ✅ Smoke Checks

```bash
python3 stego_cli.py hidden --text "Garden 42" --method base64 --json
python3 Hidden/cli.py --text "Plan a city garden schedule" --method masked --position second --len 6 --seed 7 --dry-run --json
python3 stego_cli.py doctor --json
```
