import logging
import os
from typing import Optional

from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler
from bhamon_development_toolkit.python.pylint_issue import PylintIssue


logger = logging.getLogger("Pylint")


class PylintOutputHandler(ProcessOutputHandler):


    def __init__(self) -> None:
        self._message_fields = [ "path", "line", "module", "obj", "msg", "msg_id", "symbol", "category" ]
        self._message_separator = "|"


    def process_stdout_line(self, line: str) -> None:
        self._handle_line_as_issue_message(line.rstrip())


    def process_stderr_line(self, line: str) -> None:
        self._handle_line_as_issue_message(line.rstrip())


    def process_stdout_end(self) -> None:
        pass


    def process_stderr_end(self) -> None:
        pass


    def get_message_template(self) -> str:
        return self._message_separator.join([ "{" + field + "}" for field in self._message_fields ])


    def _handle_line_as_issue_message(self, line: str) -> None:
        issue = self._parse_issue_message(line)
        if issue is not None:
            log_level = self._get_log_level_for_issue(issue)
            logger.log(log_level, "(%s:%s) %s (%s, %s)", issue.file_path, issue.line_in_file, issue.message, issue.identifier, issue.code)


    def _parse_issue_message(self, line: str) -> Optional[PylintIssue]:
        if self._message_separator not in line:
            return None

        issue_as_dict = {}

        message_elements = line.split(self._message_separator)
        for index, field in enumerate(self._message_fields):
            issue_as_dict[field] = message_elements[index]

        return PylintIssue(
            identifier = issue_as_dict["symbol"],
            code = issue_as_dict["msg_id"],
            category = issue_as_dict["category"],
            message = issue_as_dict["msg"],
            file_path = os.path.relpath(issue_as_dict["path"]),
            line_in_file = int(issue_as_dict["line"]),
            obj = issue_as_dict["obj"],
        )


    def _get_log_level_for_issue(self, issue: PylintIssue) -> int:
        if issue.category in [ "error", "fatal" ]:
            return logging.ERROR
        if issue.category in [ "convention", "refactor", "warning" ]:
            return logging.WARNING

        raise ValueError("Unhandled issue category '%s'" % issue.category)
