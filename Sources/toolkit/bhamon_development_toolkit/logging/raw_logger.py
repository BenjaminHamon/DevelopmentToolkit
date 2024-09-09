import logging
from typing import Optional, TextIO

from bhamon_development_toolkit.logging import logging_helpers


class RawLogger:


    def __init__(self, name: Optional[str] = None) -> None:
        if name is None:
            name = "raw"

        self._logger = logging.Logger(name, logging.DEBUG)


    def get_actual_logger(self) -> logging.Logger:
        return self._logger


    def __enter__(self) -> "RawLogger":
        return self


    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.dispose()


    def configure_log_stream(self, stream: TextIO, level: str) -> None:
        logging_helpers.configure_log_stream(self._logger, stream, level, "{message}", logging_helpers.date_format_iso)


    def configure_log_file(self, file_path: str, level: str, mode: str, encoding: str) -> None:
        logging_helpers.configure_log_file(self._logger, file_path, level, "{message}", logging_helpers.date_format_iso, mode, encoding)


    def dispose(self) -> None:
        for handler in list(self._logger.handlers):
            self._logger.removeHandler(handler)
            handler.close()
