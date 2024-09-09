import shlex
from typing import List, Optional, TextIO

from bhamon_development_toolkit.logging.raw_logger import RawLogger


def format_executable_command(command: List[str]):
    return " ".join(format_executable_command_element(element) for element in command)


def format_executable_command_element(element: str) -> str:
    return shlex.quote(element)


def create_raw_logger(stream: Optional[TextIO] = None, log_file_path: Optional[str] = None) -> RawLogger:
    raw_logger = RawLogger()

    if stream is not None:
        raw_logger.configure_log_stream(stream, "info")

    if log_file_path is not None:
        raw_logger.configure_log_file(log_file_path, "debug", mode = "w", encoding = "utf-8")

    return raw_logger
