from transformers import GPT2TokenizerFast, GPT2LMHeadModel
import torch
import math
from tqdm import tqdm
import json
import os
import numpy as np

from utils.logger import setup_logger

class GPT2LM:
    def __init__(self, model_path):
        """
        Initializes the GPT2LM model with the provided model path.

        :param str model_path: Path to the pre-trained GPT-2 model.
        """
        self.tokenizer = GPT2TokenizerFast.from_pretrained(model_path)
        self.lm = GPT2LMHeadModel.from_pretrained(model_path)
        if torch.cuda.is_available():
            self.lm.cuda()

    def __call__(self, sentence):
        """
        Calculate the fluency (perplexity) of a given sentence.

        :param str sentence: A sentence for which to calculate fluency.
        :return: Perplexity (exp of the loss).
        :rtype: float
        """
        # Tokenize the input sentence
        inputs = self.tokenizer(sentence, return_tensors="pt", max_length=512, truncation=True)
        input_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']

        # Move inputs to GPU if available
        if torch.cuda.is_available():
            input_ids, attention_mask = input_ids.cuda(), attention_mask.cuda()

        # Compute the loss and return the perplexity (exp of the loss)
        loss = self.lm(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)[0]
        return math.exp(loss.item())

if __name__ == "__main__":
    # set logger
    logger = setup_logger(log_filename="PPL_Test.log",current_dir=os.path.dirname(__file__))

    # Load model configuration from config.json
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, "r") as f:
        config = json.load(f)
        
    # Initialize the GPT2LM model with the path to the pre-trained model
    local_model_path = config["model_path"]
    lm = GPT2LM(model_path=local_model_path)

    # Load input data from JSON file
    with open(config["input_file"], 'r', encoding='utf-8') as file:
        input_data = json.load(file)
    logger.info(f"Test File: {config['input_file']}  Test Item: {config['item']}")
    # List to store perplexities for all sentences
    all_ppl = []

    # Compute perplexity for each sentence in the input data
    with torch.no_grad():
        for item in tqdm(input_data):
            sentence = item[config["item"]]
            sentence_ppl = lm(sentence)
            all_ppl.append(sentence_ppl)

        # Calculate average perplexity delta
        avg_ppl_delta = np.average(all_ppl)

    # Output the average perplexity
    logger.info(f"Average Perplexity Delta: {avg_ppl_delta:.4f}")
    print(f"Average Perplexity Delta: {avg_ppl_delta:.4f}")
