import logging
import os
import shlex
from typing import List, Optional, TextIO

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner
from bhamon_development_toolkit.processes.process_status import ProcessStatus


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


async def run(
        spawner: ProcessSpawner,
        command: ExecutableCommand,
        options: ProcessOptions,
        output_handlers: Optional[List[ProcessOutputHandler]] = None,
        check_exit_code: bool = True
        ) -> ProcessStatus:

    watcher = await spawner.spawn_process(command = command, options = options)

    if output_handlers is not None:
        for handler in output_handlers:
            watcher.add_output_handler(handler)

    try:
        await watcher.start()
        await watcher.wait()
        await watcher.complete(check_exit_code)

    except BaseException as exception:
        if watcher.get_status().is_running:
            await watcher.terminate(type(exception).__name__)

        raise

    return watcher.get_status()
