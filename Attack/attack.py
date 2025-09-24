
import os
import json
import random
import logging
from tqdm import tqdm
import re
import datetime
# Feedback enhancement and matching functions
from feedback_enhance import (
    enhance_encrypted_output,
    enhance_decryption_problem,
    diversify_information_hiding_scenarios,
    enhance_malicious_question_transformation
)
from feedback_match import (
    content_harm_judge,
    qr_content_harm_judge,
    repeat_question,
    refuse_response,
    relative_original
)
# Utility functions
from utils.word_util import extract_first_words, extract_Caesar_words, extract_Morse_words
from utils.logger import setup_logger
from utils.config import read_config
from utils.data_process import read_csv_data, read_txt, read_json
from Attack.information_hidden import generate_hidden_paragraph
from utils.model import Generate
from Evaluation.PPL.gpt_model import GPT2LM


def main():
    config = read_config(os.path.join(os.path.dirname(__file__), 'config.json'))
    logger = setup_logger(log_file_path=config["log_filename"], logger_name="main_logger")
    logger.info("======== StegoLLM Attack Task Started ========")
    debug_logger = setup_logger(log_file_path=config["debug_log_filename"], level=logging.DEBUG, logger_name="debug_logger")
    # Load dataset
    data = read_csv_data(config["input_data_path"], config["input_data_key"])

    # Import prompt components
    prefix_org = read_json(config["prefix_path"])[config["position"]]
    example_screen_org = read_json(config["example_screen_path"])[config["position"]]
    suffix_org = read_json(config["suffix_path"])
    suffix_reword = {"Hidden Sentence": 0, "Morse Code": 0, "Caesar Code": 0}
    relative_original_reword = {"Encode_Change": 0, "Screen_Change": 0}

    # Load hyperparameters from config
    MAX_RETRIES = config.get("max_retries", 6)
    TEMPERATURE_MIN = config.get("temperature_min", 0.6)
    TEMPERATURE_MAX = config.get("temperature_max", 1.3)
    MAX_TOKENS = config.get("max_tokens", 8192)
    DEFAULT_SCREEN_TYPE = config.get("default_screen_type", "novel_magic")
    
    results = []
    # output file with timestamp and model type
    orig_output = config["output_path"]
    model_type = config.get("attack_target_model_type", "unknown")
    safe_model_type = re.sub(r'[^\w\-\.]', '_', str(model_type)).strip('_')
    time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    base, ext = os.path.splitext(orig_output)
    new_output = f"{base}_{time_str}_{safe_model_type}{ext}"

    for text in tqdm(data, desc="Processing StegoLLM attacks"):
        # Initialize variables for each input
        last_valid_response = None
        last_valid_reason = None
        last_valid_response_abstract = None
        reinforce_encrypted_output = False
        malicious_question_transformation = False

        # Generate initial prompt components
        prefix = prefix_org
        example_screen = example_screen_org
        suffix_index = random.choice(list(suffix_reword.keys()))  # avoid always picking the same
        suffix = suffix_org[suffix_index]
        relative_original_index = random.choice(list(relative_original_reword.keys()))
        input_text = text
        screen_type = DEFAULT_SCREEN_TYPE

        for attempt in range(MAX_RETRIES):
            # Generate the hidden paragraph using the information hiding model
            hidden_paragraph = generate_hidden_paragraph(
                input_text,
                screen_type,
                config["auxiliary_model_type"],
                config["auxiliary_model_apikey"],
                logger,
                debug_logger,
                position=config["position"],
            )

            # Construct the full query for the attack
            hidden_query = f"{prefix}{example_screen}\nQuestion:\nInput:[{hidden_paragraph}]{suffix}"
            logger.info(f"Suffix_reword {suffix_reword}")
            logger.info(f"Jailbreak_query: ")

            # Generate the model response
            temperature = round(random.uniform(TEMPERATURE_MIN, TEMPERATURE_MAX), 1)
            response, reason = Generate(
                hidden_query,
                config["attack_target_model_type"],
                temperature,
                MAX_TOKENS,
                config["attack_target_api_key"],
                logger,
                debug_logger
            )

            if response:
                last_valid_response, last_valid_reason = response, reason

                # Response Content Encryption Capability Judge
                response_content = False
                if suffix_index in ["Caesar Code", "Morse Code"]:
                    if "Sure" in response:
                        response_content = True
                else:
                    response_content = content_harm_judge(
                        response,
                        config["judge_model_type"],
                        config["judge_model_key"],
                        logger,
                        debug_logger
                    )
                    
                if response_content:
                    if not reinforce_encrypted_output:  # Reinforce the Requirement for Encrypted Output
                        prefix = enhance_encrypted_output(prefix)
                        reinforce_encrypted_output = True
                        logger.info("Reinforce the Requirement for Encrypted Output.")
                    else:  # Change the Encryption Method
                        suffix_reword[suffix_index] -= 1
                        other_suffixes = {k: v for k, v in suffix_reword.items() if k != suffix_index}
                        suffix_index = max(other_suffixes, key=other_suffixes.get)
                        suffix = suffix_org[suffix_index]
                        prefix = prefix_org
                        reinforce_encrypted_output = False
                        logger.info(f"Change the Encryption Method. {suffix_index}")
                    continue

                # Decode the response
                if suffix_index == "Caesar Code":
                    abstract = extract_Caesar_words(response)
                elif suffix_index == "Morse Code":
                    abstract = extract_Morse_words(response)
                else:
                    abstract = extract_first_words(response)
                logger.info(f"Abstract_words: {abstract}")
                last_valid_response_abstract = abstract

                # Abstract content harm judge
                abstract_content = qr_content_harm_judge(
                    text,
                    abstract,
                    config["judge_model_type"],
                    config["judge_model_key"],
                    logger,
                    debug_logger
                )
                if not abstract_content:
                    # Bypass Content Safety Mechanisms
                    if refuse_response(response, logger):
                        logger.info("Response was refused — attempting malicious question transformation.")
                        if not malicious_question_transformation:
                            input_text = enhance_malicious_question_transformation(
                                input_text,
                                config["judge_model_type"],
                                config["judge_model_key"],
                                logger,
                                debug_logger
                            )
                            malicious_question_transformation = True
                            logger.info("Malicious question transformation applied.")
                        else:
                            # Diversify Information Hiding Scenarios
                            screen_type = diversify_information_hiding_scenarios(screen_type)
                            malicious_question_transformation = False
                            input_text = text
                            logger.info("Switched hiding scenario and reset input text.")
                        continue

                    # Problem Decryption Capability
                    elif not relative_original(
                        abstract,
                        input_text,
                        config["judge_model_type"],
                        config["judge_model_key"],
                        logger,
                        debug_logger
                    ):
                        logger.info(f"current_relative_index:{relative_original_index}; "
                                    f"relative_original_reword: {relative_original_reword} \n ")
                        relative_original_index = max(
                            relative_original_reword, key=relative_original_reword.get
                        )
                        if relative_original_index == "Encode_Change":
                            suffix_reword[suffix_index] -= 1
                            other_suffixes = {k: v for k, v in suffix_reword.items() if k != suffix_index}
                            suffix_index = max(other_suffixes, key=other_suffixes.get)
                            suffix = suffix_org[suffix_index]
                            prefix = prefix_org
                            reinforce_encrypted_output = False
                            logger.info(f"Change the Encryption Method. {suffix_index}")
                        else:
                            # Diversify Information Hiding Scenarios
                            screen_type = diversify_information_hiding_scenarios(screen_type)
                            malicious_question_transformation = False
                            input_text = text
                            logger.info("Switched hiding scenario and reset input text.")
                            relative_original_reword[relative_original_index] -= 1
                            continue

                    elif repeat_question(abstract, text):
                        logger.info("Problem decryption failed — enhancing decryption capability.")
                        example_screen = enhance_decryption_problem(example_screen)
                        continue
                    
                    else:
                        # Malicious Question Transformation fallback
                        logger.info("Response was refused — attempting malicious question transformation.")
                        if not malicious_question_transformation:
                            input_text = enhance_malicious_question_transformation(
                                input_text,
                                config["judge_model_type"],
                                config["judge_model_key"],
                                logger,
                                debug_logger
                            )
                            malicious_question_transformation = True
                            logger.info("Malicious question transformation applied.")
                        else:
                            screen_type = diversify_information_hiding_scenarios(screen_type)
                            malicious_question_transformation = False
                            input_text = text
                            logger.info("Switched hiding scenario and reset input text.")
                        continue

                else:
                    suffix_reword[suffix_index] += 1
                    relative_original_reword[relative_original_index] += 1
                    break

        # collect results for this input
        results.append({
            "query": text,
            "hidden question": hidden_query,
            "hidden question answer": last_valid_response,
            "reason": last_valid_reason,
            "response_abstract": last_valid_response_abstract
        })

        # Write results to output file after all inputs processed
        with open(new_output, "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    main()
