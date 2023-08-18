from typing import Optional


class ProcessException(Exception):


    def __init__(self, message: str, executable: str, exit_code: Optional[int]) -> None:
        super().__init__(message)
        self.executable = executable
        self.exit_code = exit_code
