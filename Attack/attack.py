import os
from tqdm import tqdm
import torch
import json
import random
from feedback_enhance import enhance_encrypted_output,enhance_decryption_problem,diversify_information_hiding_scenarios,enhance_malicious_question_transformation
from feedback_match import content_harm_judge,qr_content_harm_judge,repeat_question, refuse_response,relative_original
from utils.word_util import extract_first_words,extract_Caesar_words,extract_Morse_words
from utils.logger import setup_logger
from utils.config import read_config
from utils.data_process import read_csv_data, read_txt,read_json
from Attack.information_hidden import generate_hidden_paragraph
from utils.model import Generate
from Evaluation.PPL.gpt_model import GPT2LM
from transformers import AutoTokenizer, AutoModelForCausalLM, DynamicCache

def main():
    config = read_config(os.path.join(os.path.dirname(__file__), 'config.json'))
    logger = setup_logger(log_filename=config["log_filename"], current_dir=os.path.dirname(__file__))
    logger.info("======== StegoLLM Attack Task Started ========")

    # Data Get
    data = read_csv_data(config["input_data_path"],config["input_data_key"])

    # Import prompt
    prefix_org = read_json(config["prefix_path"])[config["position"]]
    example_screen_org = read_json(config["example_screen_path"])[config["position"]]
    suffix_org = read_json(config["suffix_path"])
    suffix_reword = {"Hidden Sentence":0,
                     "Morse Code":0,
                     "Caesar Code":0
                     }
    relative_original_reword = {"Encode_Change":0,
                            "Screen_Change":0}
    # MODEL_NAME = config["model_file_path"]
    # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # llm = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16, device_map="auto")

    max_retries = config["max_retries"]
    results = []
    for text in tqdm(data, desc="Processing StegoLLM attacks"):
        # init
        last_valid_response = None
        last_valid_reason = None
        last_valid_response_abstract = None
        reinforce_encrypted_output = False
        malicious_question_transformation = False
        
        #Generate initial prompt
        prefix = prefix_org
        example_screen = example_screen_org
        suffix_index = max(suffix_reword, key=suffix_reword.get)
        suffix = suffix_org[suffix_index]
        relative_original_index = max(relative_original_reword, key=relative_original_reword.get)
        input_text = text
        screen_type = "novel_magic"

        for attempt in range(max_retries):
            hidden_paragraph = generate_hidden_paragraph(input_text, screen_type, config["model_type_hidden"], config["api_key_hidden"], logger,position=config["position"])
            

            hidden_query = f"{prefix}{example_screen}\nQuestion: \nInput:[{hidden_paragraph}]{suffix}"
            logger.info(f"hidden_query: {hidden_query} /n suffix_reword{suffix_reword}")
            tempeture = round(random.uniform(0.6, 1.3), 1)
            response, reason = Generate(hidden_query, config["model_type_target"], tempeture, 8192, config["api_key_target"],logger)
            
            if response:
                last_valid_response, last_valid_reason= response, reason
                # Response Content Encryption Capability Judge
                response_content = False
                if suffix_index=="Caesar Code" or suffix_index=="Morse Code":
                    if "Sure" in response:
                        response_content = True
                else:
                    response_content = content_harm_judge(response,config["judge_model_type"], config["judge_model_key"],logger)
                    

                if response_content:
                    if not reinforce_encrypted_output:#Reinforce the Requirement for Encrypted Output
                        prefix = enhance_encrypted_output(prefix)
                        reinforce_encrypted_output == True
                        logger.info("Reinforce the Requirement for Encrypted Output.")

                    else:# Change the Encryption Method
                        suffix_reword[suffix_index] -=1
                        other_suffixes = {k: v for k, v in suffix_reword.items() if k != suffix_index}
                        suffix_index = max(other_suffixes, key=other_suffixes.get)
                        suffix = suffix_org[suffix_index]
                        prefix = prefix_org
                        reinforce_encrypted_output == False
                        logger.info(f"Change the Encryption Method. {suffix_index}")

                    continue

                # Decode the response
                if suffix_index=="Caesar Code":
                    abstract = extract_Caesar_words(response)
                elif suffix_index=="Morse Code":
                    abstract = extract_Morse_words(response)
                else:
                    abstract = extract_first_words(response)
                logger.info(f"abstract_words: {abstract}")
                last_valid_response_abstract = abstract

                abstract_content = qr_content_harm_judge(text, abstract,config["judge_model_type"], config["judge_model_key"],logger)
                if not abstract_content:
                    # Bypass Content Safety Mechanisms
                    if refuse_response(response,logger):
                        logger.info("Response was refused — attempting malicious question transformation.")
                        # Malicious Question Transformation
                        if not malicious_question_transformation:
                            input_text = enhance_malicious_question_transformation(input_text,config["judge_model_type"], config["judge_model_key"],logger)
                            malicious_question_transformation=True
                            logger.info("Malicious question transformation applied.")
                        else:
                            # Diversify Information Hiding Scenarios
                            screen_type = diversify_information_hiding_scenarios(screen_type)
                            malicious_question_transformation= False
                            input_text = text
                            logger.info("Switched hiding scenario and reset input text.")
                        continue

                    # Problem Decryption Capability
                    elif not relative_original(abstract,input_text,config["judge_model_type"], config["judge_model_key"],logger):
                        logger.info(f"current_relative_index:{relative_original_index}; relative_original_reword: {relative_original_reword} /n ")
                        relative_original_index = max(relative_original_reword, key=relative_original_reword.get)
                        if relative_original_index == "Encode_Change":
                            suffix_reword[suffix_index] -=1
                            other_suffixes = {k: v for k, v in suffix_reword.items() if k != suffix_index}
                            suffix_index = max(other_suffixes, key=other_suffixes.get)
                            suffix = suffix_org[suffix_index]
                            prefix = prefix_org
                            reinforce_encrypted_output == False
                            
                            logger.info(f"Change the Encryption Method. {suffix_index}")
                        else:
                            #Diversify Information Hiding Scenarios
                            screen_type = diversify_information_hiding_scenarios(screen_type)
                            malicious_question_transformation= False
                            input_text = text
                            logger.info("Switched hiding scenario and reset input text.")
                            relative_original_reword[relative_original_index] -=1
                            continue

                    elif repeat_question(abstract,text):
                        logger.info("Problem decryption failed — enhancing decryption capability.")
                        example_screen = enhance_decryption_problem(example_screen)
                        continue
                    
                    # Bypass Content Safety Mechanisms
                    else:
                        # Malicious Question Transformation
                        logger.info("Response was refused — attempting malicious question transformation.")
                        # Malicious Question Transformation
                        if not malicious_question_transformation:
                            input_text = enhance_malicious_question_transformation(input_text,config["judge_model_type"], config["judge_model_key"],logger)
                            malicious_question_transformation=True
                            logger.info("Malicious question transformation applied.")
                        else:
                            # Diversify Information Hiding Scenarios
                            screen_type = diversify_information_hiding_scenarios(screen_type)
                            malicious_question_transformation= False
                            input_text = text
                            logger.info("Switched hiding scenario and reset input text.")
                        continue

                else:
                    suffix_reword[suffix_index] +=1
                    relative_original_reword[relative_original_index] +=1
                    break

        results.append(
            { "query": text, 
                "hidden question": hidden_query, 
                "hidden question answer": last_valid_response, 
                "reason": last_valid_reason, 
                "response_abstract":last_valid_response_abstract
            }
                )


        with open(config["output_file"], "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
