import logging
import os
import datetime
from datetime import datetime

LOG_DIR_NAME = "logs"
LOG_FORMAT = "%(asctime)s [%(threadName)s/%(levelname)s]: %(message)s"
TIME_FORMAT = "%m-%d-%y %H-%M-%S"

log_fmt = logging.Formatter(LOG_FORMAT)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(
    f"{os.path.join(os.getcwd(), LOG_DIR_NAME, datetime.utcnow().strftime(TIME_FORMAT))}.log")

stream_handler.setFormatter(log_fmt)
file_handler.setFormatter(log_fmt)

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

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

        return logger

def set_logger(logger: logging.Logger) -> None:
    """
    Removes all other loggers, and adds
    stream_handler and file_handler to the given logger

    This is being used for sanic logging, because
    for some weird reason sanic does not allow you
    to pass in a custom logging object. Instead, you have
    to modify their logger, or use logging.dictConfig.

    :param logger: The logger object to modify
    :type logger: logging.Logger
    """

    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

def set_access_logger(logger: logging.Logger) -> None:
    """
    Does basically the same thing as set_logger
    but for the access_logger, because it needs different formatting

    :param logger: The access logger to modify
    :type logger: logging.Logger
    """
    for handler in logger.handlers:
        logger.removeHandler(handler)

    log_access_format = "%(asctime)s [%(threadName)s/%(levelname)s]: %(request)s request made from %(host)s"

    access_log_handler = logging.StreamHandler()
    access_log_handler.setFormatter(logging.Formatter(log_access_format))

    access_file_handler = logging.FileHandler(
        f"{os.path.join(os.getcwd(), LOG_DIR_NAME, datetime.utcnow().strftime(TIME_FORMAT))}.log")
    access_file_handler.setFormatter(logging.Formatter(log_access_format))

    logger.addHandler(access_log_handler)
    logger.addHandler(access_file_handler)

