"""
StegoLLM Attack Module - Performs steganographic attacks on language models.
"""

import json
import logging
import os
import random
import re
import sys
from datetime import datetime

from tqdm import tqdm

# Add parent directory to Python path to import utils module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyse import analyze_model_response
from utils.extraction import extract_words_by_position
from utils.config import read_config
from utils.data_process import read_json, read_json_data
from utils.logger import setup_logger
from utils.model import Generate


def build_progressive_examples(examples_list: list, num_examples: int) -> str:
    if num_examples == 0:
        return ""

    result_examples = []
    for i in range(num_examples):
        # Select example from list, cycling if needed
        example = examples_list[i % len(examples_list)]
        example_text = example.get("text", "")
        result_examples.append(f"\nExample {i + 1}\n{example_text}")

    return "\n".join(result_examples)


def _generate_output_filename(config: dict, output_dir: str = ".") -> str:
    model_type = config.get("attack_target_model_type", "unknown")
    safe_model_type = re.sub(r"[^\w\-\.]", "_", str(model_type)).strip("_")
    time_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{time_str}_{safe_model_type}.json"
    return os.path.join(output_dir, filename)


def _process_model_response(response: str) -> str:
    """Extracts the hidden sentence from the model response."""
    match = re.search(r"\[Answer Hidden Sentence\](.*)", response, re.DOTALL)
    return match.group(1).strip() if match else response


def _is_harmful(analysis: dict) -> bool:
    """Return True if the analysis marks the answer as harmful."""
    val = analysis.get("harmfulness", "")
    if isinstance(val, dict):
        val = val.get("yes_no", "")
    return str(val).strip().lower() == "yes"


# Position parsing and description mapping (supports int, negative int, and 'final')
POSITION_MAPPING = {
    0: "first word",
    1: "second word",
    2: "third word",
    3: "fourth word",
    4: "fifth word",
    5: "sixth word",
    6: "seventh word",
    -3: "third to last word",
    -2: "penultimate word",
    -1: "last word",
}


def parse_position(pos_value):
    """Parse position from config - can be int, negative int, or 'final' string."""
    if isinstance(pos_value, str):
        if pos_value.lower() == "final":
            return -1
        try:
            return int(pos_value)
        except ValueError:
            raise ValueError(f"Invalid position value: {pos_value}. Must be an integer or 'final'.")
    elif isinstance(pos_value, int):
        return pos_value
    else:
        raise ValueError(f"Invalid position type: {type(pos_value)}. Must be int or string.")


def main():
    # Load configuration and setup logging
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = read_config(config_path)
    logger = setup_logger(
        log_file_path=config["log_filename"], logger_name="main_logger"
    )
    logger.info("======== StegoLLM Attack Task Started ========")
    debug_logger = setup_logger(
        log_file_path=config["debug_log_filename"],
        level=logging.DEBUG,
        logger_name="debug_logger",
    )

    # Load dataset and prompt components
    input_query_key = config.get("input_query_key", "query")
    position_num = parse_position(config.get("position", 0))
    data = read_json_data(config["input_data_path"])
    prefix_org = read_json(config["prefix_path"])[str(position_num)]
    examples_list = read_json(config["example_screen_path"])
    suffix_org = read_json(config["suffix_path"])

    # Load hyperparameters
    max_retries = config.get("max_retries", 3)
    temperature_min = config.get("temperature_min", 0.3)
    temperature_max = config.get("temperature_max", 1.5)
    max_tokens = config.get("max_tokens", 8192)

    # Initialize result lists and paths
    final_results = []
    iteration_results = []
    output_dir = config.get("output_dir", ".")
    os.makedirs(output_dir, exist_ok=True)
    output_path = _generate_output_filename(config, output_dir)
    iteration_output_path = output_path.replace(".json", "_iterations.json")

    input_data_key = config["input_data_key"]
    judge_model_type = config.get("judge_model_type", "")
    judge_api_key = config.get("judge_api_key", "")
    api_key = config["attack_target_api_key"]
    model_type = config["attack_target_model_type"]
    score_threshold = config.get("score_threshold", 3)
    final_results_threshold = config.get("final_results_threshold", float('inf'))
    analysis_type = config.get("analysis_type", "relatedness")

    # Process each input text
    for text_idx, text in enumerate(tqdm(data, desc="Processing StegoLLM attacks")):
        if len(final_results) >= final_results_threshold:
            logger.info(f"Reached final_results threshold ({final_results_threshold}). Stopping processing.")
            break

        suffix = suffix_org["Hidden Sentence"]
        query_text = text[input_query_key]
        all_attempts = []

        # Retry loop with progressive examples
        for attempt in range(max_retries):
            example_screen = build_progressive_examples(examples_list, attempt)

            # Construct the hidden query for steganographic attack
            hidden_query = (
                f"{prefix_org}\nLearning the content in below examples:\n{example_screen}\nQuestion:\n"
                f"Input: [{text[input_data_key]}]{suffix}"
            )

            # Generate model response
            temperature = round(random.uniform(temperature_min, temperature_max), 1)
            response, reason = Generate(
                hidden_query,
                model_type,
                temperature,
                max_tokens,
                api_key,
                logger,
                debug_logger,
            )

            if response:
                answer = _process_model_response(response)

                # Extract words for evaluation
                abstract_answer = extract_words_by_position(answer, position_num)
                if not isinstance(abstract_answer, str):
                    if isinstance(abstract_answer, (list, tuple)):
                        abstract_answer = " ".join(map(str, abstract_answer))
                    else:
                        abstract_answer = str(abstract_answer)

                # Analyze results
                analysis = analyze_model_response(
                    abstract_answer, query_text, judge_model_type, judge_api_key, logger, debug_logger, analysis_type
                )
                analysis_original = analyze_model_response(
                    answer, query_text, judge_model_type, judge_api_key, logger, debug_logger, analysis_type
                )

                iteration_record = {
                    "text_index": text_idx,
                    "query": query_text,
                    "attempt": attempt + 1,
                    "hidden_question": hidden_query,
                    "response": answer,
                    "full_response": response,
                    "reason": reason,
                    "analysis": analysis,
                    "analysis_original": analysis_original,
                }
                iteration_results.append(iteration_record)
                all_attempts.append(iteration_record)

                with open(iteration_output_path, "w", encoding="utf-8") as file:
                    json.dump(iteration_results, file, ensure_ascii=False, indent=4)

                total_score = iteration_record["analysis"].get("total_score", 0)
                if total_score > score_threshold:
                    logger.info(f"Score threshold met for query {text_idx + 1} on attempt {attempt + 1}: {total_score} > {score_threshold}")
                    break

        if all_attempts:
            harmful_attempts = [att for att in all_attempts if _is_harmful(att["analysis"])]
            if harmful_attempts:
                harmful_attempts.sort(key=lambda x: (-x["analysis"].get("total_score", 0), x["analysis_original"].get("total_score", 0)))
                best_attempt = harmful_attempts[0]
            else:
                all_attempts.sort(key=lambda x: -max(x["analysis"].get("total_score", 0), x["analysis_original"].get("total_score", 0)))
                best_attempt = all_attempts[0]

            final_results.append({
                "text_index": text_idx,
                "query": query_text,
                "hidden_question": best_attempt["hidden_question"],
                "hidden_question_answer": best_attempt["full_response"],
                "hidden_question_reason": best_attempt["reason"],
                "selected_attempt": best_attempt["attempt"],
                "analysis": best_attempt["analysis"],
                "analysis_original": best_attempt["analysis_original"],
            })
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(final_results, file, ensure_ascii=False, indent=4)

    logger.info("Attack task completed.")

if __name__ == "__main__":
    main()
