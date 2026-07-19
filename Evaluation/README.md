# Evaluation

> Evaluation tools for StegoAttack outputs, grouped by folder and model dependency.

## Overview

| Folder | Quality axis | Purpose |
| --- | --- | --- |
| `PPL/` | Linguistic quality / stealth | Measures fluency with GPT-2 perplexity. |
| `Grammar/` | Linguistic quality / stealth | Counts grammar issues with LanguageTool. |
| `ASR/` | Semantic quality / harmfulness | Computes attack success from existing relatedness and harmfulness fields. |
| `Detectors/` | Semantic quality / harmfulness | Stores external guard references; no local guard adapter is implemented. |

For a machine-readable list of model downloads and invocation examples:

```bash
python3 stego_cli.py eval-models --json
```

## 1. PPL

`PPL/` evaluates linguistic stealth by measuring whether generated text remains
fluent under a language model.

- Script: `Evaluation/PPL/PPL_Text.py`
- Metric: average perplexity
- Model: `openai-community/gpt2`
- Download: https://huggingface.co/openai-community/gpt2

Set `Evaluation/PPL/config.json`:

```json
{
  "model_path": "openai-community/gpt2",
  "input_file": "path/to/results.json",
  "item": "answer_hidden_response"
}
```

Run:

```bash
python3 Evaluation/PPL/PPL_Text.py
```

You may also set `model_path` to a local Hugging Face snapshot path.

## 2. Grammar

`Grammar/` evaluates linguistic stealth by counting grammar issues in generated
text.

- Script: `Evaluation/Grammar/Grammar.py`
- Metric: average grammar error count
- Runtime dependency: `language_tool_python`

Set `Evaluation/Grammar/config.json`:

```json
{
  "language_type": "en-US",
  "input_file": "path/to/results.json",
  "item": "answer_hidden_response"
}
```

Run:

```bash
python3 Evaluation/Grammar/Grammar.py
```

`language_tool_python` may download or start a local LanguageTool backend on
first use, but this is not an LLM evaluation.

## 3. ASR

`ASR/` evaluates semantic quality from existing model-judge outputs. It checks
whether a response is both related to the request and harmful.

- Scripts: `Evaluation/ASR/ASR_Test.py`, `Evaluation/ASR/reduction.py`
- Metrics: ASR, relatedness score, harmfulness score, guard reduction
- Required input: result JSON files with `analysis` or `analysis_original`
  fields

Run:

```bash
python3 stego_cli.py asr --folder Attack/Results --json
```

If detector summaries are available, compute ASR reduction:

```bash
python3 stego_cli.py guard-reduction \
  --asr-folder Attack/Results \
  --detector-summary path/to/detector_summary.json \
  --json
```

ASR does not call a model. Any model judging must already have been written into
the result JSON files before running this step.

## 4. Detectors

`Detectors/` does not implement LlamaGuard, ShieldLM, or WildGuard locally. It
only records model references and the expected external-summary workflow.

Example external serving command:

```bash
vllm serve allenai/wildguard
```

After running the detector outside this repository, export a summary JSON and
use it for ASR reduction:

```bash
python3 stego_cli.py guard-reduction \
  --asr-folder Attack/Results \
  --detector-summary path/to/detector_summary.json \
  --json
```

Expected summary fields:

```json
{
  "detector": "wildguard",
  "mode": "external",
  "total": 100,
  "unsafe_count": 25,
  "unsafe_rate": 0.25,
  "results": []
}
```

Detector model links:

| Detector | Model | Download |
| --- | --- | --- |
| LlamaGuard | `meta-llama/Llama-Guard-3-8B` | https://huggingface.co/meta-llama/Llama-Guard-3-8B |
| ShieldLM | `thu-coai/ShieldLM-7B-internlm2` | https://huggingface.co/thu-coai/ShieldLM-7B-internlm2 |
| WildGuard | `allenai/wildguard` | https://huggingface.co/allenai/wildguard |
