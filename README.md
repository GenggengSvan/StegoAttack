# StegoAttack

![Jailbreak Attacks](https://img.shields.io/badge/Jailbreak-Attacks-yellow.svg?style=plastic)
![Adversarial Attacks](https://img.shields.io/badge/Adversarial-Attacks-orange.svg?style=plastic)
![Large Language Models](https://img.shields.io/badge/LargeLanguage-Models-green.svg?style=plastic)

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)


## Overview

This repository shares the code of our latest work on LLMs jailbreaking. In this work:

- We reveals that current jailbreak attacks struggle to achieve both semantic stealth and linguistic stealth simultaneously, and are often insufficient in terms of attack potency.

<p align="center">
  <img src="image/background.png" width="700"/>
</p>


- We introduce *StegoAttack*, a fully stealthy jailbreak framework that employs steganographic techniques to embed harmful queries within benign texts. We ensure the attack's effectiveness by integrating a comprehensive system-level framework.

- We compare *StegoAttack* with eight jailbreak methods across four state-of-the-art LLMs (such as GPT-5 and DeepSeek-R1). The results show that *StegoAttack* not only achieves high success rates but also operates stealthily, effectively circumventing both the built-in and external safety mechanisms. 


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
export LLM_BASE_URL="https://api.deepseek.com"
export LLM_MODEL="deepseek-v4-pro"
```

When using the DeepSeek direct API, prefer `deepseek-v4-pro`. Provider-prefixed
names such as `deepseek/deepseek-v4-pro` are normalized for the direct DeepSeek
base URL.

### 2. Steganographic Generation Pipeline (Hidden)
Generate natural sentences containing specific hidden words via Masked Regeneration.
- **Single text**:
  ```bash
  export LLM_API_KEY="..."
  python3 stego_cli.py hidden \
    --text "Plan a city garden schedule" \
    --method masked \
    --position second \
    --model deepseek-v4-pro \
    --base-url https://api.deepseek.com/v1 \
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
    --json
  ```
- **Batch file**:
  ```bash
  python Hidden/cli.py --input Data/Advbench-50/harmful_behaviors.csv --key query --position second --len 10
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
    --input Hidden/Hidden_Output/result_harmful_behaviors_masked_first.json \
    --position first \
    --model deepseek-v4-pro \
    --base-url https://api.deepseek.com/v1 \
    --json
  ```
- **Configuration**: `Attack/config.json` still provides defaults, but runtime
  arguments such as `--text`, `--input`, `--output`, `--model`, `--base-url`,
  `--judge-model`, `--analysis-type`, and `--max-retries` override it.

### 4. Multi-dimensional Evaluation (Evaluation)
Evaluate the performance of generated steganographic text in terms of ASR. `Evaluation/ASR/ASR_Test.py`

> **Note**: Ensure the `input_file` path is correctly set in the respective `config.json` before running evaluation scripts.
