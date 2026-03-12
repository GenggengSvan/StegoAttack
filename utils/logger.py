# utils/logger.py
import logging
import logging.handlers
import os
from typing import Optional

DEFAULT_LOG_FILENAME = "attack.log"
DEFAULT_LOG_DIRNAME = "Output"

def setup_logger(
    log_file_path: Optional[str] = None,
    level: int = logging.INFO,
    console: bool = True,
    rotating: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    logger_name: Optional[str] = None,
) -> logging.Logger:
    """
    Create and return a configured logger.

    Args:
        log_file_path: full path to the log file OR a directory.
        level: logging level.
        console: whether to also log to console.
        rotating: whether to use RotatingFileHandler.
        max_bytes, backup_count: for RotatingFileHandler.
        logger_name: unique name for logger (so we can create multiple loggers).
    """
    if logger_name is None:
        logger_name = os.path.basename(log_file_path) if log_file_path else DEFAULT_LOG_FILENAME

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False  # prevent double logging

    # Avoid duplicate handlers if already created
    if logger.handlers:
        return logger

    # Determine file path
    if log_file_path:
        if os.path.isdir(log_file_path):
            log_dir = log_file_path
            log_file_path = os.path.join(log_dir, DEFAULT_LOG_FILENAME)
        else:
            log_dir = os.path.dirname(os.path.abspath(log_file_path))
            if not log_dir:
                log_dir = os.getcwd()
                log_file_path = os.path.join(log_dir, log_file_path)
    else:
        this_dir = os.path.dirname(os.path.abspath(__file__))      
        project_root = os.path.dirname(this_dir)                   
        default_output_dir = os.path.join(project_root, "Attack", DEFAULT_LOG_DIRNAME)
        log_dir = default_output_dir
        log_file_path = os.path.join(log_dir, DEFAULT_LOG_FILENAME)

    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    if rotating:
        fh = logging.handlers.RotatingFileHandler(
            filename=log_file_path,
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
    else:
        fh = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


if __name__ == "__main__":
    log1 = setup_logger("Output/log1.log", logger_name="log1")
    log2 = setup_logger("Output/log2.log", logger_name="log2")
    log1.info("Message from log1")
    log2.info("Message from log2")
