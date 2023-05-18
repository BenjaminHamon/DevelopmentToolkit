import asyncio
from asyncio.subprocess import Process as ProcessImplementation
import signal
from typing import Optional

from bhamon_development_toolkit.processes.process import Process


class ProcessWrapper(Process):


    def __init__(self, implementation: ProcessImplementation, termination_signal: signal.Signals) -> None:
        self._implementation = implementation
        self._termination_signal = termination_signal


    @property
    def pid(self) -> int:
        return self._implementation.pid


    @property
    def stdout(self) -> Optional[asyncio.StreamReader]:
        return self._implementation.stdout


    @property
    def stderr(self) -> Optional[asyncio.StreamReader]:
        return self._implementation.stderr


    @property
    def exit_code(self) -> Optional[int]:
        return self._implementation.returncode


    @property
    def is_running(self) -> bool:
        return self._implementation.returncode is None


    async def wait(self) -> int:
        return await self._implementation.wait()


    def terminate(self) -> None:
        self._implementation.send_signal(self._termination_signal)


    def kill(self) -> None:
        self._implementation.kill()
