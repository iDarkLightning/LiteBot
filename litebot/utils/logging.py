import logging
import os
import datetime
from datetime import datetime

LOG_DIR_NAME = "logs"
LOG_FORMAT = "%(asctime)s [%(threadName)s/%(levelname)s]: %(message)s"
TIME_FORMAT = "%m-%d-%y %H-%M-%S"

def get_logger(name: str) -> logging.Logger:
    """
    Gets a logger with correct formatting
    Includes stream handlers and file handler handlers

    Example Format
    ---------------
        2021-03-05 20:01:18,504 [MainThread/INFO]: Message

    :param name: The name of the logger
    :type name: str
    :return: A logger object
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger
    else:
        logger.setLevel(logging.DEBUG)
        log_fmt = logging.Formatter(LOG_FORMAT)

        stream_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(
            f"{os.path.join(os.getcwd(), LOG_DIR_NAME, datetime.utcnow().strftime(TIME_FORMAT))}.log")

        stream_handler.setFormatter(log_fmt)
        file_handler.setFormatter(log_fmt)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

        return logger
