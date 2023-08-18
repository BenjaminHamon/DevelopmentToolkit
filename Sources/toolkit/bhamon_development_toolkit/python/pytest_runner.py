import json
import logging
import os
import shutil
from typing import List, Optional

from bhamon_development_toolkit.processes import process_helpers
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_logger import ProcessOutputLogger
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.python.pytest_output_handler import PytestOutputHandler
from bhamon_development_toolkit.python.pytest_scope import PytestScope


logger = logging.getLogger("Pytest")


class PytestRunner:


    def __init__(self, process_runner: ProcessRunner, python_executable: str) -> None:
        self._process_runner = process_runner
        self._python_executable = python_executable


    async def run(self, # pylint: disable = too-many-arguments
            all_scopes: List[PytestScope], run_identifier: str, base_result_directory: str,
            working_directory: Optional[str] = None, simulate: bool = False) -> None:

        if len(all_scopes) == 0:
            raise ValueError("all_scopes must not be empty")

        logger.info("Running tests (RunIdentifier: '%s')", run_identifier)

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
            logger.info("Pytest session completed successfully")
        if not session_success:
            raise RuntimeError("Pytest session completed with failures")


    async def _run_with_scope(self,
            scope: PytestScope, result_directory: str, working_directory: Optional[str] = None, simulate: bool = False) -> bool:

        log_file_path = os.path.join(result_directory, scope.identifier + ".log")
        json_report_file_path = os.path.join(result_directory, scope.identifier + ".json")

        command = ExecutableCommand(self._python_executable)
        command.add_internal_arguments([ "-u" ], [])
        command.add_arguments([ "-m", "pytest", scope.path ])
        command.add_arguments([ "--basetemp", os.path.join(result_directory, scope.identifier) ])
        command.add_arguments([ "-k", scope.filter_expression ] if scope.filter_expression is not None else [])
        command.add_internal_arguments([ "--verbose", "--verbose" ], [])
        command.add_internal_arguments([ "--json", os.path.abspath(json_report_file_path) ] if not simulate else [], [])

        process_options = ProcessOptions(working_directory = working_directory)
        raw_output_logger = ProcessOutputLogger(process_helpers.create_raw_logger(log_file_path = log_file_path))
        pytest_output_handler = PytestOutputHandler(scope)

        logger.info("+ %s", process_helpers.format_executable_command(command.get_command_for_logging()))

        success = True

        if not simulate:
            status = await self._process_runner.run(command, process_options, [ raw_output_logger, pytest_output_handler ], check_exit_code = False)

            self._check_exit_code(status.exit_code)
            success = self._get_success_from_exit_code(status.exit_code)

            with open(json_report_file_path, mode = "r", encoding = "utf-8") as json_report_file:
                json_report = json.load(json_report_file)
            with open(json_report_file_path + ".tmp", mode = "w", encoding = "utf-8") as json_report_file:
                json.dump(json_report, json_report_file, indent = 4)
            os.replace(json_report_file_path + ".tmp", json_report_file_path)

        return success


    def _check_exit_code(self, exit_code: Optional[int]) -> None:
        if exit_code is None:
            raise RuntimeError("Exit code should not be none")

        if exit_code == 0: # All tests were collected and passed successfully
            return
        if exit_code == 1: # Tests were collected and run but some of the tests failed
            return
        if exit_code == 2: # Test execution was interrupted by the user
            raise KeyboardInterrupt("Pytest execution was interrupted")
        if exit_code == 3: # Internal error happened while executing tests
            raise RuntimeError("Pytest internal error")
        if exit_code == 4: # pytest command line usage error
            raise RuntimeError("Pytest usage error")
        if exit_code == 5: # No tests were collected
            return

        raise ValueError("Unsupported Pytest exit code: '%s'" % exit_code)


    def _get_success_from_exit_code(self, exit_code: Optional[int]) -> bool:
        if exit_code is None:
            raise RuntimeError("Exit code should not be none")

        if exit_code == 0: # All tests were collected and passed successfully
            return True
        if exit_code == 1: # Tests were collected and run but some of the tests failed
            return False
        if exit_code == 5: # No tests were collected
            return True

        raise ValueError("Unsupported Pytest exit code: '%s'" % exit_code)
