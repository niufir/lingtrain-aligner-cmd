import os

import logging


def getLogger4Run(pathRootDir:str) -> logging.Logger:

    log_dir = os.path.join(pathRootDir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_name = 'log_run'

    file_handler = logging.FileHandler(os.path.join(log_dir, log_name + '.log'), encoding = 'utf-8')
    file_handler.setLevel(logging.INFO)

    # Create a logger with a unique name
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)  # Set the log level at the logger level

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger