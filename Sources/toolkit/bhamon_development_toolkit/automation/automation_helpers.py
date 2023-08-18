import argparse
import contextlib
import importlib
import logging
import os
import sys
from typing import Generator, Optional

from bhamon_development_toolkit.automation.automation_command import AutomationCommand
from bhamon_development_toolkit.logging import logging_helpers


@contextlib.contextmanager
def execute_in_workspace(workspace_root_directory: str) -> Generator[None,None,None]:
    current_directory = os.getcwd()
    os.chdir(workspace_root_directory)

    try:
        yield
    finally:
        os.chdir(current_directory)


def configure_logging(arguments: argparse.Namespace):
    message_format = "{asctime} [{levelname}][{name}] {message}"
    date_format = "%Y-%m-%dT%H:%M:%S"

    log_stream_verbosity: str = "info"
    log_file_path: Optional[str] = None
    log_file_verbosity: str = "debug"

    if arguments is not None and getattr(arguments, "verbosity", None) is not None:
        log_stream_verbosity = arguments.verbosity
    if arguments is not None and getattr(arguments, "log_file", None) is not None:
        log_file_path = arguments.log_file
    if arguments is not None and getattr(arguments, "log_file_verbosity", None) is not None:
        log_file_verbosity = arguments.log_file_verbosity

    logging.root.setLevel(logging.DEBUG)

    logging.addLevelName(logging.DEBUG, "Debug")
    logging.addLevelName(logging.INFO, "Info")
    logging.addLevelName(logging.WARNING, "Warning")
    logging.addLevelName(logging.ERROR, "Error")
    logging.addLevelName(logging.CRITICAL, "Critical")

    logging_helpers.configure_log_stream(sys.stdout, log_stream_verbosity, message_format, date_format)
    if log_file_path is not None:
        logging_helpers.configure_log_file(log_file_path, log_file_verbosity, message_format, date_format, mode = "w", encoding = "utf-8")


def create_argument_parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--simulate", action = "store_true",
        help = "perform a test run, without writing changes")
    argument_parser.add_argument("--verbosity", choices = logging_helpers.all_log_levels,
        metavar = "<level>", help = "set the logging level (%s)" % ", ".join(logging_helpers.all_log_levels))
    argument_parser.add_argument("--log-file",
        metavar = "<file_path>", help = "set the log file path")
    argument_parser.add_argument("--log-file-verbosity", choices = logging_helpers.all_log_levels,
        metavar = "<level>", help = "set the logging level for the log file (%s)" % ", ".join(logging_helpers.all_log_levels))

    return argument_parser


def create_command_instance(class_fully_qualified_name: str) -> AutomationCommand:
    module_full_name, class_name = class_fully_qualified_name.rsplit(".", 1)
    module = importlib.import_module(module_full_name)
    class_from_module = getattr(module, class_name)

    command_instance = class_from_module()
    if not isinstance(command_instance, AutomationCommand):
        raise ValueError("The class '%s' does not implement the AutomationCommand interface" % class_fully_qualified_name)

    return command_instance
