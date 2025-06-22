import logging
import os


def get_file_current_file_directory() -> str:
    current_file_path = os.path.abspath(__file__)
    return os.path.dirname(current_file_path)


g_logger: logging.Logger = None


def getLogger4Test() -> logging.Logger:
    global g_logger
    if g_logger is not None:
        return g_logger

    log_dir = os.path.join(get_file_current_file_directory(), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = logging.FileHandler(os.path.join(log_dir, 'log_testing.log'), encoding = 'utf-8')
    file_handler.setLevel(logging.INFO)

    # Create a logger with a unique name
    g_logger = logging.getLogger('Test_Aligner')
    g_logger.setLevel(logging.INFO)  # Set the log level at the logger level

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    g_logger.addHandler(file_handler)
    g_logger.addHandler(console_handler)

    return g_logger


# Initialize the logger


