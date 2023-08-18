import logging
import os
import shutil
from typing import List, Optional

from bhamon_development_toolkit.processes import process_helpers
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_logger import ProcessOutputLogger
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.python.pylint_output_handler import PylintOutputHandler
from bhamon_development_toolkit.python.pylint_scope import PylintScope


logger = logging.getLogger("Pylint")


class PylintRunner:


    def __init__(self, process_runner: ProcessRunner, python_executable: str) -> None:
        self._process_runner = process_runner
        self._python_executable = python_executable


    async def run(self, # pylint: disable = too-many-arguments
            all_scopes: List[PylintScope], run_identifier: str, base_result_directory: str,
            working_directory: Optional[str] = None, simulate: bool = False) -> None:

        if len(all_scopes) == 0:
            raise ValueError("all_scopes must not be empty")

        logger.info("Running linter (RunIdentifier: '%s')", run_identifier)

        result_directory = os.path.join(base_result_directory, run_identifier)

        if not simulate:
            if os.path.exists(result_directory):
                shutil.rmtree(result_directory)
            os.makedirs(result_directory)

        session_success = True

        for scope in all_scopes:
            success_for_scope = await self._run_with_scope(scope, result_directory, working_directory = working_directory, simulate = simulate)
            if not success_for_scope:
                session_success = False

        logger.debug("Result directory: '%s'", result_directory)

        if session_success:
            logger.info("Pylint session completed successfully")
        if not session_success:
            raise RuntimeError("Pylint session completed with issues")


    async def _run_with_scope(self,
            scope: PylintScope, result_directory: str, working_directory: Optional[str] = None, simulate: bool = False) -> bool:

        log_file_path = os.path.join(result_directory, scope.identifier + ".log")
        json_report_file_path = os.path.join(result_directory, scope.identifier + ".json")

        command = ExecutableCommand(self._python_executable)
        command.add_internal_arguments([ "-u" ], [])
        command.add_arguments([ "-m", "pylint", scope.path_or_module ])
        command.add_internal_arguments([ "--output-format=text,json:%s" % os.path.abspath(json_report_file_path) ], [])

        process_options = ProcessOptions(working_directory = working_directory)
        raw_output_logger = ProcessOutputLogger(process_helpers.create_raw_logger(log_file_path = log_file_path))
        pylint_output_handler = PylintOutputHandler()

        command.add_internal_arguments([ "--msg-template", pylint_output_handler.get_message_template() ], [])

        logger.info("+ %s", process_helpers.format_executable_command(command.get_command_for_logging()))

        success = True

        if not simulate:
            status = await self._process_runner.run(command, process_options, [ raw_output_logger, pylint_output_handler ], check_exit_code = False)

            self._check_exit_code(status.exit_code)
            success = self._get_success_from_exit_code(status.exit_code)

        return success


    def _check_exit_code(self, exit_code: Optional[int]) -> None:
        if exit_code is None:
            raise RuntimeError("Exit code should not be none")

        if exit_code == 0:
            return
        if 0 < exit_code < 32: # Bit flags corresponding to messages issues
            return
        if exit_code == 32:
            raise RuntimeError("Pylint usage error")

        raise ValueError("Unsupported Pytest exit code: '%s'" % exit_code)


    def _get_success_from_exit_code(self, exit_code: Optional[int]) -> bool:
        if exit_code is None:
            raise RuntimeError("Exit code should not be none")

        if exit_code == 0:
            return True
        if 0 < exit_code < 32:
            return False

        raise ValueError("Unsupported Pytest exit code: '%s'" % exit_code)
