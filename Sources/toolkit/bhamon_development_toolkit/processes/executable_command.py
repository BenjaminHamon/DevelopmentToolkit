import os
from typing import List


class ExecutableCommand:


    def __init__(self, executable: str) -> None:
        self._executable = executable
        self._arguments: List[str] = []
        self._arguments_for_logging: List[str] = []


    def add_arguments(self, arguments: List[str]) -> None:
        self._arguments += arguments
        self._arguments_for_logging += arguments


    def add_internal_arguments(self, arguments: List[str], arguments_for_logging: List[str]) -> None:
        self._arguments += arguments
        self._arguments_for_logging += arguments_for_logging


    @property
    def executable_name(self) -> str:
        return os.path.basename(self._executable)


    @property
    def executable_path(self) -> str:
        return self._executable


    def get_command(self) -> List[str]:
        return [ self._executable ] + self._arguments


    def get_command_for_logging(self) -> List[str]:
        return [ self._executable ] + self._arguments_for_logging
