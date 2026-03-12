import torch
import math
from transformers import GPT2TokenizerFast, GPT2LMHeadModel


# Method one: PPL
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