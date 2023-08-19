import logging
import os
import re
from typing import Optional

from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler
from bhamon_development_toolkit.python.pytest_result import PytestResult
from bhamon_development_toolkit.python.pytest_scope import PytestScope


logger = logging.getLogger("Pytest")


class PytestOutputHandler(ProcessOutputHandler):


    def __init__(self, scope: PytestScope) -> None:
        self._scope = scope

        status_collection = [ "passed", "failed", "skipped", "error", "xpassed", "xfailed" ]
        status_collection_regex = "|".join(x.upper() for x in status_collection)

        self._test_result_regex = re.compile(r"^(?P<identifier>.*)\s+(?P<status>" + status_collection_regex + r")\s+\[\s*[0-9]+%\]$")


    def process_stdout_line(self, line: str) -> None:
        self._handle_line_as_test_result(line.rstrip())


    def process_stderr_line(self, line: str) -> None:
        self._handle_line_as_test_result(line.rstrip())


    def process_stdout_end(self) -> None:
        pass


    def process_stderr_end(self) -> None:
        pass


    def _handle_line_as_test_result(self, line: str) -> None:
        test_result = self._parse_test_result(line)
        if test_result is not None:
            log_level = self._get_log_level_for_test_result(test_result)
            logger.log(log_level, "Test '%s' completed with status '%s'", test_result.identifier, test_result.status)


    def _parse_test_result(self, line: str) -> Optional[PytestResult]:
        match = re.search(r"^(?P<identifier>.*) (?P<status>[A-Z]+) \[\s*[0-9]+%\]", line)
        if match is None:
            return None

        result_as_dict = match.groupdict()

        return PytestResult(
            identifier = os.path.relpath(result_as_dict["identifier"], self._scope.path).replace(".py::", ".").replace("\\", ".").replace("/", "."),
            status = result_as_dict["status"].lower(),
        )


    def _get_log_level_for_test_result(self, result: PytestResult) -> int:
        if result.status in [ "passed", "skipped", "xfailed" ]:
            return logging.INFO
        if result.status in [ "error", "failed", "xpassed" ]:
            return logging.ERROR

        raise ValueError("Unhandled pytest result status '%s'" % result.status)
