import logging

from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler


class ProcessOutputLogger(ProcessOutputHandler):


    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger


    def process_stdout_line(self, line: str) -> None:
        self._logger.debug(line.rstrip())


    def process_stderr_line(self, line: str) -> None:
        self._logger.debug(line.rstrip())


    def process_stdout_end(self) -> None:
        pass


    def process_stderr_end(self) -> None:
        pass
