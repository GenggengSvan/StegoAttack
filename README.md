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


- We introduce *StegoAttack*, a fully stealthy jailbreak framework that employs steganographic techniques to embed harmful queries within benign texts. We ensure the attack's effectiveness by integrating a comprehensive system-level framework that dynamically adapts the attack template based on model responses.

- We compare *StegoAttack* with eight jailbreak methods across four state-of-the-art LLMs (such as OpenAI-o3 and DeepSeek-R1). The results show that *StegoAttack* not only achieves high success rates but also operates stealthily, effectively circumventing both the built-in and external safety mechanisms. 


<p align="center">
  <img src="image/StegoAttack.png" width="700"/>
</p>


## Getting Started


**1. Build Environment**
```shell
conda create -n StegoAttack python=3.9
conda activate StegoAttack
pip install -r requirements.txt
```

**2. Modify Parameters**
All parameters used by StegoAttack are specified in `Attack/config.json`, including:

`log_filename`: execution log path
`debug_log_filename`: detailed log path for model calls
`input_data_path`: path to the input data file (e.g., CSV with attack queries)
`input_data_key`: column name in the input data file containing the queries
`auxiliary_model_type`: model type used for generating information-hiding paragraphs
`auxiliary_model_apikey`: API key for the auxiliary model
`attack_target_model_type`: model type to be attacked
`attack_target_api_key`: API key for the attack target model
`judge_model_type`: model type used for response evaluation in dynamic feedback
`judge_model_key`: API key for the judge model
`max_retries`: maximum number of retries for feedback
`position`: position to insert the hidden information (e.g., "first","last","second","fifth","last second")
`prefix_path`: path to the prefix template file
`example_screen_path`: path to the example template file for information hiding
`suffix_path`: path to the suffix template file
`output_path`: path to save the attack results
`<model_type>_url`: custom URL for a model if not included in BASE_URLS in model.py (e.g., "glm-4.5_url")

**Note**: StegoAttack uses `deepseek-chat` to generate information-hiding paragraphs, and also utilizes `deepseek-chat` as the model for response evaluation during the dynamic feedback process. 

You can switch these two models to any models you have access to. Simply modify the `auxiliary_model_type` and `judge_model_type parameters` in `config.json` and provide the corresponding API KEY. 

If the model's URL is not in `BASE_URLS` in `model.py`, add the new model's URL to `config.json` in the format `"<attack_target_model_type>_url":"<url>"`.



**3. Run StegoAttack**
```shell 
pip install -e .
python .\Attack\attack.py
```

**4. Get Responses**
Both the log and the input JSON file are located in the Output folder.
`hidden question` answer is the model’s response.
`response_abstract` is the decrypted result, used to evaluate the ASR.