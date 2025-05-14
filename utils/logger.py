import logging
import os

def setup_logger(log_filename='model_output.log',current_dir= os.path.dirname(os.path.abspath(__file__))):
    """
    Set up the logger for logging outputs to a file and console.

    :param log_filename: The name of the log file (default: 'model_output.log')
    :return: logger instance
    """
    log_file_path = os.path.join(current_dir, log_filename)

    logger = logging.getLogger('GPT2LM')
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger