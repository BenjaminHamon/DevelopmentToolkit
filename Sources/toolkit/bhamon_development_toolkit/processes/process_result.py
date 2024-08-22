import dataclasses
import os
import subprocess
from typing import Optional


@dataclasses.dataclass(frozen = True)
class ProcessResult:


    @staticmethod
    def create_from_completed_process(completed_process: subprocess.CompletedProcess) -> "ProcessResult":
        return ProcessResult(
            executable = completed_process.args[0],
            exit_code = completed_process.returncode,
            standard_output = completed_process.stdout,
            error_output = completed_process.stderr,
        )


    executable: str
    exit_code: int
    standard_output: Optional[str] = None
    error_output: Optional[str] = None


    @property
    def executable_name(self) -> str:
        return os.path.basename(self.executable)


    @property
    def executable_path(self) -> str:
        return self.executable
