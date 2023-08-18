import asyncio
import datetime
from typing import Optional

from bhamon_development_toolkit.processes.process import Process


class FakeProcess(Process):


    def __init__(self, # pylint: disable = too-many-arguments
            pid: int,
            execution_duration: datetime.timedelta,
            stdout: Optional[asyncio.StreamReader] = None,
            stderr: Optional[asyncio.StreamReader] = None,
            exit_code_for_normal_completion: int = 0,
            allow_termination: bool = True) -> None:

        self._pid = pid
        self._stdout = stdout
        self._stderr = stderr
        self._execution_duration = execution_duration
        self._exit_code_for_normal_completion = exit_code_for_normal_completion
        self._allow_termination = allow_termination

        self._exit_code: Optional[int] = None
        self._is_alive: bool = True


    @property
    def pid(self) -> int:
        return self._pid


    @property
    def stdout(self) -> Optional[asyncio.StreamReader]:
        return self._stdout


    @property
    def stderr(self) -> Optional[asyncio.StreamReader]:
        return self._stderr


    @property
    def exit_code(self) -> Optional[int]:
        return self._exit_code


    @property
    def is_running(self) -> bool:
        return self._is_alive


    async def wait(self) -> int:
        if not self._is_alive:
            if self._exit_code is None:
                raise RuntimeError("Exit code should not be none")
            return self._exit_code

        await asyncio.sleep(self._execution_duration.total_seconds())

        self._is_alive = False
        self._exit_code = self._exit_code_for_normal_completion

        return self._exit_code


    def terminate(self) -> None:
        if not self._allow_termination:
            return

        self._is_alive = False
        self._exit_code = -1


    def kill(self) -> None:
        self._is_alive = False
        self._exit_code = -2
