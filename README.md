# StegoAttack

![Jailbreak Attacks](https://img.shields.io/badge/Jailbreak-Attacks-yellow.svg?style=plastic)
![Adversarial Attacks](https://img.shields.io/badge/Adversarial-Attacks-orange.svg?style=plastic)
![Large Language Models](https://img.shields.io/badge/LargeLanguage-Models-green.svg?style=plastic)

**Project Page:** https://genggengsvan.github.io/StegoAttack/

## Table of Contents

- [Project Page](https://genggengsvan.github.io/StegoAttack/)
- [Overview](#overview)
- [Quick Usage Guide](#-quick-usage-guide)


## Overview

This repository shares the code for our work on LLM jailbreaking. In this work:

- We reveal that current jailbreak attacks struggle to achieve both semantic stealth and linguistic stealth simultaneously, and are often insufficient in terms of attack potency.

<p align="center">
  <img src="image/background.png" width="700"/>
</p>


- We introduce *StegoAttack*, a fully stealthy jailbreak framework that employs steganographic techniques to embed harmful queries within benign texts. We ensure the attack's effectiveness by integrating a comprehensive system-level framework.

- We compare *StegoAttack* with eight jailbreak methods across four state-of-the-art LLMs, including GPT-5, Gemini-3, DeepSeek-V3.2, and Qwen3-max. The results show that *StegoAttack* not only achieves high success rates but also operates stealthily, effectively circumventing both built-in and external safety mechanisms.


<p align="center">
  <img src="image/StegoAttack.png" width="700"/>
</p>


---

## 🚀 Quick Usage Guide


**1. Build Environment**
```shell
conda create -n StegoAttack python=3.9
conda activate StegoAttack
pip install -r requirements.txt
```

Model settings can be supplied without editing JSON files:

```bash
export LLM_API_KEY="..."
export LLM_BASE_URL="https://your-openai-compatible-endpoint/v1"
export LLM_MODEL="your-model-name"
```

`LLM_BASE_URL` must point to an OpenAI-compatible Chat Completions API endpoint.
The repository does not ship provider URL defaults. If you use the DeepSeek
direct API, model aliases such as `deepseek-pro-v4` / `deepseek-flash-v4` are
mapped to the official API names when the base URL contains `api.deepseek.com`.

### 2. Steganographic Generation Pipeline (Hidden)
Generate natural sentences containing specific hidden words via Masked Regeneration.
- **Single text**:
  ```bash
  export LLM_API_KEY="..."
  python3 stego_cli.py hidden \
    --text "Plan a city garden schedule" \
    --method masked \
    --position second \
    --model your-model-name \
    --base-url https://your-openai-compatible-endpoint/v1 \
    --output Hidden/Hidden_Output/result_custom.json \
    --json
  ```
- **Single text without model call**:
  ```bash
  python3 stego_cli.py hidden \
    --text "Plan a city garden schedule" \
    --method masked \
    --position second \
    --len 8 \
    --seed 42 \
    --dry-run \
    --output Hidden/Hidden_Output/result_custom.json \
    --json
  ```
- **Batch file**:
  ```bash
  python3 stego_cli.py hidden \
    --input Data/Advbench-50/harmful_behaviors.csv \
    --key query \
    --method masked \
    --position second \
    --len 10 \
    --limit 5 \
    --dry-run \
    --output Hidden/Hidden_Output/result_advbench_demo.json \
    --json
  ```
- **Arguments**:
  - `--text`: One input string to hide.
  - `--input`: Input file (CSV/JSON) for batch mode.
  - `--model`, `--api-key`, `--base-url`: OpenAI-compatible model settings.
  - `--position`: Target word position (`first`, `second`, `last`, `penultimate`, or integer index).
  - `--len`: Target sentence length.


### 3. Steganographic Attack (Attack)
Embed harmful instructions into model responses using steganography.
- **Preview one prompt without model calls**:
  ```bash
  python3 stego_cli.py attack \
    --text "breeze **Plan** orbit drift apple river." \
    --query "Plan a city garden schedule" \
    --position second \
    --max-retries 1 \
    --dry-run \
    --json
  ```
- **Batch run**:
  ```bash
  python3 stego_cli.py attack \
    --input Hidden/Hidden_Output/result_custom.json \
    --position second \
    --model your-model-name \
    --base-url https://your-openai-compatible-endpoint/v1 \
    --json
  ```
- **Configuration**: `Attack/config.json` still provides defaults, but runtime
  arguments such as `--text`, `--input`, `--output`, `--model`, `--base-url`,
  `--judge-model`, `--analysis-type`, and `--max-retries` override it.

### 4. Multi-dimensional Evaluation (Evaluation)
Evaluation is organized into four folders:

- `Evaluation/PPL/`: linguistic stealth via GPT-2 perplexity. Set `Evaluation/PPL/config.json`, then run `python3 Evaluation/PPL/PPL_Text.py`.
- `Evaluation/Grammar/`: linguistic stealth via grammar error count. Set `Evaluation/Grammar/config.json`, then run `python3 Evaluation/Grammar/Grammar.py`.
- `Evaluation/ASR/`: semantic quality and harmfulness from existing judge fields. Run `python3 stego_cli.py asr --folder Attack/Results --json`.
- `Evaluation/Detectors/`: external guard references. Local guard adapters are not shipped; export detector summaries and run `python3 stego_cli.py guard-reduction --asr-folder Attack/Results --detector-summary path/to/detector_summary.json --json`.

For model download links and invocation examples:

```bash
python3 stego_cli.py eval-models --json
```

> **Note**: PPL and Grammar require `input_file` and `item` in their respective `config.json` files. ASR does not call a model; it reads completed attack result JSON files.
