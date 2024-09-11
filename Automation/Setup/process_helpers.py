import logging
import shlex
import subprocess
from typing import List, Optional


def format_executable_command(command: List[str]):
    return " ".join(format_executable_command_element(element) for element in command)


def format_executable_command_element(element: str) -> str:
    return shlex.quote(element)


def run_simple(logger: logging.Logger, command: List[str], working_directory: Optional[str] = None, simulate: bool = False) -> None:
    logger.debug("+ %s", format_executable_command(command))

    subprocess_options = {
        "cwd": working_directory,
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "stdin": subprocess.DEVNULL,
    }

    if not simulate:
        result = subprocess.run(command, check = False, **subprocess_options)
        for line in result.stdout.splitlines():
            logger.debug(line)
        for line in result.stderr.splitlines():
            logger.error(line)

        if result.returncode != 0:
            raise RuntimeError("Subprocess failed (Executable: '%s', ExitCode: %s)" % (command[0], result.returncode))
