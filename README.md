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


### 2. Steganographic Generation Pipeline (Hidden)
Generate natural sentences containing specific hidden words via Masked Regeneration.
- **Run**:
  ```bash
  python Hidden/main_pipeline.py --input Data/Advbench-50/harmful_behaviors.csv --key query --position second --len 10
  ```
- **Arguments**:
  - `--input`: Input file (CSV/JSON).
  - `--position`: Target word position (`first`, `second`, `last`, `penultimate`).
  - `--len`: Target sentence length.


### 3. Steganographic Attack (Attack)
Embed harmful instructions into model responses using steganography.
- **Run**:
  ```bash
  cd Attack
  python attack.py
  ```
- **Configuration**: Modify `Attack/config.json` to set `input_data_path` (data), `attack_target_model_type` (target model), and `position` (hidden position).

### 4. Multi-dimensional Evaluation (Evaluation)
Evaluate the performance of generated steganographic text in terms of ASR. `Evaluation/ASR/ASR_Test.py`

> **Note**: Ensure the `input_file` path is correctly set in the respective `config.json` before running evaluation scripts.
