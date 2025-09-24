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
  <img src="image/background.png" width="400"/>
</p>


- We introduce *StegoAttack*, a fully stealthy jailbreak framework that employs steganographic techniques to embed harmful queries within benign texts. We ensure the attack's effectiveness by integrating a comprehensive system-level framework that dynamically adapts the attack template based on model responses.

- We compare *StegoAttack* with eight jailbreak methods across four state-of-the-art LLMs (such as OpenAI-o3 and DeepSeek-R1). The results show that *StegoAttack* not only achieves high success rates but also operates stealthily, effectively circumventing both the built-in and external safety mechanisms. 


<p align="center">
  <img src="image/StegoAttack.png" width="400"/>
</p>


## Getting Started


**1. Build Environment**
```shell
conda create -n StegoAttack python=3.9
conda activate StegoAttack
pip install -r requirements.txt
```

**2. Run StegoAttack**
   
