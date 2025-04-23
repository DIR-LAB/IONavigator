import logging
import os


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


def setup_logger(name):
    if not os.environ.get('ION_LOG_DIR'):
        print("ION_LOG_DIR not set, logging to console for", name)
        
        # Set up level
        if not os.environ.get('ION_LOG_LEVEL'):
            print("ION_LOG_LEVEL not set, using INFO level for", name)
            level = logging.INFO
        else:
            level = parse_level(os.environ.get('ION_LOG_LEVEL'))
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Create console handler with formatter
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
        return logger

    if not os.environ.get('ION_LOG_LEVEL'):
        print("ION_LOG_LEVEL not set, using INFO level for ", name)
        level = logging.INFO
    else:
        level = parse_level(os.environ.get('ION_LOG_LEVEL'))
    log_file_path = os.path.join(os.environ.get('ION_LOG_DIR'), "ION", f"{name}.log")
    if os.path.exists(log_file_path):
        # clear the file
        with open(log_file_path, 'w') as f:
            f.truncate(0)

    print(log_file_path)
    # Ensure the directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')

    # File Handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger