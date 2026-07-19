# Attack

> Wrap a Hidden-stage payload with the paper's attack prompt template, send it
> to the target model, and optionally score the response.

## ⚡ One-Liner

Preview one attack prompt without calling a model:

```bash
python3 stego_cli.py attack \
  --text "breeze **Plan** orbit drift apple river." \
  --query "Plan a city garden schedule" \
  --position second \
  --dry-run \
  --json
```

Run against an OpenAI-compatible target model:

```bash
export LLM_API_KEY="your-api-key"

python3 stego_cli.py attack \
  --input Hidden/Hidden_Output/result_custom.json \
  --position second \
  --model your-model-name \
  --base-url https://your-openai-compatible-endpoint/v1 \
  --judge-model deepseek-chat \
  --max-retries 3 \
  --json
```

## 🎛️ Inputs

- `--text`: one steganographic payload to inject into the attack template. Best
  for quick prompt preview.
- `--query`: original query label for `--text` mode. Defaults to `--text`.
- `--input`: JSON list from the Hidden stage.
- `--output`: exact final JSON path.
- `--output-dir`: directory for timestamped result files.

## 🧪 Useful Smoke Mode

`--dry-run` writes the constructed prompt and skips all model calls:

```bash
python3 stego_cli.py attack \
  --text "breeze **Plan** orbit drift apple river." \
  --query "Plan a city garden schedule" \
  --position second \
  --max-retries 1 \
  --dry-run \
  --json
```

## 🤖 Model Options

- `--model`, `--api-key`, `--base-url`: target model settings.
- `--judge-model`, `--judge-api-key`, `--judge-base-url`: evaluation model settings.
- `--analysis-type`: `relatedness`, `harmfulness`, or `both`.
- `--score-threshold`: stop retrying once a score exceeds this value.
- `--temperature-min`, `--temperature-max`: random sampling range per retry.
- `--max-retries`: progressive-example retry count.

Prefer `LLM_API_KEY`, `LLM_MODEL`, and `LLM_BASE_URL` for local runs so secrets
do not land in shell history.

## 🗂️ Files

- `attack.py`: CLI and attack runner.
- `analyse.py`: target-response scoring helpers.
- `config.json`: default paths, model names, thresholds, and template paths.
- `template/`: prefix, suffix, and in-context examples used by the prompt.
