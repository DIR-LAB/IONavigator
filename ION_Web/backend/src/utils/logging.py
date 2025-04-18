import logging
from logging.handlers import RotatingFileHandler
import os


LOG_DIR = "logs"

def parse_level(level):
    if level == "INFO":
        return logging.INFO
    elif level == "DEBUG":
        return logging.DEBUG
    elif level == "WARNING":
        return logging.WARNING
    elif level == "ERROR":
        return logging.ERROR
    else:
        raise ValueError(f"Invalid log level: {level}")


def setup_logger(name, log_level="INFO"):
    log_level = parse_level(log_level)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create formatters
    #file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')
    file_formatter = logging.Formatter('%(module)s - %(funcName)s - %(message)s')
    log_file_path = os.path.join(LOG_DIR, f"{name}.log")
    if os.path.exists(log_file_path):
        # clear the file
        with open(log_file_path, 'w') as f:
            f.truncate(0)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    

    # File Handler
    file_handler = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=2)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Stream Handler (stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(file_formatter)
    logger.addHandler(stream_handler)

    return logger





