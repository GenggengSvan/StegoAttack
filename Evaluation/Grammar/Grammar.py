import json
from tqdm import tqdm
import numpy as np
import language_tool_python
import os

from utils.logger import setup_logger

class GrammarChecker:
    def __init__(self,language_type):
        self.lang_tool = language_tool_python.LanguageTool(language_type)

    def check(self, sentence):
        '''
        :param sentence:  a string
        :return:
        '''
        matches = self.lang_tool.check(sentence)
        return len(matches)


if __name__ == "__main__":
    # set logger
    logger = setup_logger(log_filename="Grammar_Test.log",current_dir=os.path.dirname(__file__))

    # Load model configuration from config.json
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, "r") as f:
        config = json.load(f)

    checker = GrammarChecker(language_type=config['language_type'])
    
    # Load input data from JSON file
    with open(config["input_file"], 'r', encoding='utf-8') as file:
        input_data = json.load(file)
    logger.info(f"Test File: {config['input_file']}  Test Item: {config['item']}")
    
    # List to store error
    all_error = []

    for item in tqdm(input_data):
        poison_error = checker.check(item[config["item"]])
        all_error.append(poison_error)
    print(all_error)
    avg_grammar_error_delta = np.average(all_error)


    logger.info(f"avg_grammar_error_delta: {avg_grammar_error_delta:.2f}")
    print(f"{avg_grammar_error_delta:.2f}")
