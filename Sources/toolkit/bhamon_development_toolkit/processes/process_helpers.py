import logging
import os
import shlex
from typing import List, Optional, TextIO


def format_executable_command(command: List[str]):
    return " ".join(format_executable_command_element(element) for element in command)


def format_executable_command_element(element: str) -> str:
    return shlex.quote(element)


def create_raw_logger(stream: Optional[TextIO] = None, log_file_path: Optional[str] = None) -> logging.Logger:
    logger = logging.Logger("raw")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("{message}", style = "{")

    if stream is not None:
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setLevel(logging.INFO)
        stream_handler.formatter = formatter
        logger.addHandler(stream_handler)

    if log_file_path is not None:
        if os.path.dirname(log_file_path):
            os.makedirs(os.path.dirname(log_file_path), exist_ok = True)
        file_handler = logging.FileHandler(log_file_path, mode = "w", encoding = "utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.formatter = formatter
        logger.addHandler(file_handler)

    return logger
