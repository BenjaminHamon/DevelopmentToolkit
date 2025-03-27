import asyncio
import logging
import shlex
import subprocess
from typing import Any, List, Optional, TextIO

from bhamon_development_toolkit.logging.raw_logger import RawLogger
from bhamon_development_toolkit.processes.exceptions.process_failure_exception import ProcessFailureException
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_result import ProcessResult


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


def run_simple(logger: logging.Logger, command: ExecutableCommand, *,
        working_directory: Optional[str] = None, check_exit_code: bool = True, simulate: bool = False) -> ProcessResult:

    logger.debug("+ %s", format_executable_command(command.get_command_for_logging()))

    subprocess_options = {
        "cwd": working_directory,
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "stdin": subprocess.DEVNULL,
    }

    if not simulate:
        result = subprocess.run(command.get_command(), check = False, **subprocess_options)
        for line in result.stdout.splitlines():
            logger.debug(line)
        for line in result.stderr.splitlines():
            logger.error(line)

        if check_exit_code and result.returncode != 0:
            exception_message = "Subprocess failed (Executable: '%s', ExitCode: %s)" % (command.executable_path, result.returncode)
            raise ProcessFailureException(exception_message, command.executable_path, result.returncode)

        return ProcessResult(
            executable = command.executable_path,
            exit_code = result.returncode,
            standard_output = result.stdout,
            error_output = result.stderr,
        )

    return ProcessResult(
        executable = command.executable_path,
        exit_code = 0,
    )


async def run_simple_async(logger: logging.Logger, command: ExecutableCommand, *,
        working_directory: Optional[str] = None, check_exit_code: bool = True, simulate: bool = False) -> ProcessResult:

    async def watch_output(stream: asyncio.StreamReader, logging_level: int) -> str:
        encoding = "utf-8"

        output = ""

        while True:
            line_as_bytes = await stream.readline()
            if not line_as_bytes:
                break

            line = line_as_bytes.decode(encoding).replace("\r\n", "\n")
            logger.log(logging_level, line.rstrip())

            output += line

        return output

    async def check_task(identifier: str, task: asyncio.Task) -> Any:
        try:
            return await asyncio.wait_for(task, 1)
        except asyncio.CancelledError:
            pass
        except asyncio.TimeoutError:
            logger.warning("Task '%s' timed out", identifier)
        except Exception: # pylint: disable = broad-except
            logger.error("Task '%s' raised an unhandled exception", identifier, exc_info = True)
        return None

    logger.debug("+ %s", format_executable_command(command.get_command_for_logging()))

    if not simulate:
        process = await asyncio.create_subprocess_exec(*command.get_command(),
            stdin = subprocess.DEVNULL, stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = working_directory)

        if process.stdout is None:
            raise RuntimeError("Process stdout should not be none")
        if process.stderr is None:
            raise RuntimeError("Process stderr should not be none")

        stdout_task = asyncio.create_task(watch_output(process.stdout, logging.DEBUG))
        stderr_task = asyncio.create_task(watch_output(process.stderr, logging.ERROR))

        exit_code = await process.wait()

        if check_exit_code and exit_code != 0:
            exception_message = "Subprocess failed (Executable: '%s', ExitCode: %s)" % (command.executable_path, exit_code)
            raise ProcessFailureException(exception_message, command.executable_path, exit_code)

        stdout_text = await check_task("stdout", stdout_task)
        stderr_text = await check_task("stderr", stderr_task)

        return ProcessResult(
            executable = command.executable_path,
            exit_code = exit_code,
            standard_output = stdout_text,
            error_output = stderr_text,
        )

    return ProcessResult(
        executable = command.executable_path,
        exit_code = 0,
    )
