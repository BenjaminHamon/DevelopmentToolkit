import dataclasses
import os
from typing import Optional


@dataclasses.dataclass(frozen = True)
class ProcessStatus:
    executable: str
    pid: int
    is_running: bool
    exit_code: Optional[int]


    @property
    def executable_name(self) -> str:
        return os.path.basename(self.executable)


    @property
    def executable_path(self) -> str:
        return self.executable
