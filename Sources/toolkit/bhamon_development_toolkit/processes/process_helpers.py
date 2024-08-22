import logging
import os
import shlex
from typing import List, Optional, TextIO

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_collector import ProcessOutputCollector
from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler
from bhamon_development_toolkit.processes.process_result import ProcessResult
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner


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
        check_exit_code: bool = True,
    ) -> ProcessResult:

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

    status = watcher.get_status()
    if status.exit_code is None:
        raise ValueError("Process exit code is not set")

    return ProcessResult(
        executable = status.executable,
        exit_code = status.exit_code,
    )


async def run_with_collector(
        spawner: ProcessSpawner,
        command: ExecutableCommand,
        options: ProcessOptions,
        check_exit_code: bool = True,
    ) -> ProcessResult:

    output_collector = ProcessOutputCollector()

    result = await run(spawner, command, options, output_handlers = [ output_collector ], check_exit_code = check_exit_code)

    return ProcessResult(
        executable = result.executable,
        exit_code = result.exit_code,
        standard_output = output_collector.get_stdout(),
        error_output = output_collector.get_stderr(),
    )
