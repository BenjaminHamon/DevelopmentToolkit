import logging

from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler


class ProcessOutputLogger(ProcessOutputHandler):


    def __init__(self, logger: logging.Logger,
            stdout_logging_level: int = logging.INFO, stderr_logging_level: int = logging.ERROR) -> None:

        self._logger = logger
        self._stdout_logging_level = stdout_logging_level
        self._stderr_logging_level = stderr_logging_level


    def process_stdout_line(self, line: str) -> None:
        self._logger.log(self._stdout_logging_level, line.rstrip())


    def process_stderr_line(self, line: str) -> None:
        self._logger.log(self._stderr_logging_level, line.rstrip())


    def process_stdout_end(self) -> None:
        pass


    def process_stderr_end(self) -> None:
        pass
