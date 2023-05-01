import logging
import os
from typing import TextIO


all_log_levels = [ "debug", "info", "warning", "error", "critical" ]


def configure_log_stream(stream: TextIO, level: str, message_format: str, date_format: str) -> None:
    formatter = logging.Formatter(fmt = message_format, datefmt = date_format, style = "{")

    stream_handler = logging.StreamHandler(stream)
    stream_handler.setLevel(logging.getLevelName(level.upper()))
    stream_handler.formatter = formatter

    logging.root.addHandler(stream_handler)


def configure_log_file( # pylint: disable = too-many-arguments
        file_path: str, level: str, message_format: str, date_format: str, mode: str, encoding: str) -> None:

    if os.path.dirname(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok = True)

    formatter = logging.Formatter(fmt = message_format, datefmt = date_format, style = "{")

    file_handler = logging.FileHandler(file_path, mode = mode, encoding = encoding)
    file_handler.setLevel(logging.getLevelName(level.upper()))
    file_handler.formatter = formatter

    logging.root.addHandler(file_handler)
