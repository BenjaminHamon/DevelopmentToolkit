import abc
import asyncio
from typing import Optional


class Process(abc.ABC):


    @property
    @abc.abstractmethod
    def pid(self) -> int:
        pass


    @property
    @abc.abstractmethod
    def stdout(self) -> Optional[asyncio.StreamReader]:
        pass


    @property
    @abc.abstractmethod
    def stderr(self) -> Optional[asyncio.StreamReader]:
        pass


    @property
    @abc.abstractmethod
    def exit_code(self) -> Optional[int]:
        """ Return the exit code from the process. If the process is running, returns None. """

    @property
    @abc.abstractmethod
    def is_running(self) -> bool:
        """ Return True if the process is running, otherwise False. """


    @abc.abstractmethod
    async def wait(self) -> int:
        """ Wait for the process to complete, and return the exit code. """


    @abc.abstractmethod
    def terminate(self) -> None:
        """ Signal the process to terminate. """


    @abc.abstractmethod
    def kill(self) -> None:
        """ Signal the system to force the process to terminate. """
