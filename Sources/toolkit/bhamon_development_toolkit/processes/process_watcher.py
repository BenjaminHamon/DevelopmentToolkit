import asyncio
import datetime
import logging
import time
from typing import List, Optional

from bhamon_development_toolkit.processes.exceptions.process_failure_exception import ProcessFailureException
from bhamon_development_toolkit.processes.exceptions.process_timeout_exception import ProcessTimeoutException
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process import Process
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler
from bhamon_development_toolkit.processes.process_status import ProcessStatus


logger = logging.getLogger("ProcessWatcher")


class ProcessWatcher: # pylint: disable = too-many-instance-attributes


    def __init__(self, process: Process, command: ExecutableCommand, options: ProcessOptions) -> None:
        self._process = process
        self._command = command
        self._options = options

        self._timeout_task: Optional[asyncio.Task] = None
        self._start_time: Optional[float] = None
        self._completion_time: Optional[float] = None
        self._last_output_time: Optional[float] = None
        self._custom_exit_code: Optional[int] = None

        self._stdout_task: Optional[asyncio.Task] = None
        self._stderr_task: Optional[asyncio.Task] = None
        self._output_handlers: List[ProcessOutputHandler] = []

        self._termination_lock = asyncio.Lock()


    @property
    def executable(self) -> str:
        return self._command.executable_name


    @property
    def executable_path(self) -> str:
        return self._command.executable_path


    @property
    def pid(self) -> int:
        return self._process.pid


    def get_status(self) -> ProcessStatus:
        return ProcessStatus(
            executable = self._command.executable_path,
            pid = self._process.pid,
            is_running = self._process.is_running,
            exit_code = self._resolve_exit_code(),
        )


    def _resolve_exit_code(self) -> Optional[int]:
        if self._custom_exit_code is not None:
            return self._custom_exit_code
        if self._process is not None:
            return self._process.exit_code
        return None


    async def start(self) -> None:
        logger.debug("Subprocess started (Executable: '%s', PID: %s)", self.executable, self.pid)

        self._start_time = time.time()
        self._last_output_time = time.time()

        self._timeout_task = asyncio.create_task(self._watch_timeout())
        if self._process.stdout is not None:
            self._stdout_task = asyncio.create_task(self._watch_stdout(self._process.stdout))
        if self._process.stderr is not None:
            self._stderr_task = asyncio.create_task(self._watch_stderr(self._process.stderr))


    async def wait(self) -> None:
        await self._process.wait()

        if self._timeout_task is not None:
            self._timeout_task.cancel()

        await self._wait_tasks()


    async def complete(self, check_exit_code: bool = True) -> None:
        if self._process.is_running:
            raise RuntimeError("Subprocess is still active")

        exit_code = self._resolve_exit_code()
        logger.debug("Subprocess exited (Executable: '%s', PID: %s, ExitCode: %s)", self.executable, self.pid, exit_code)

        self._completion_time = time.time()

        if exit_code != 0:
            try:
                self._check_timeouts()
            except TimeoutError as exception:
                raise ProcessTimeoutException(str(exception), self.executable, exit_code) from exception

            if check_exit_code:
                exception_message = "Subprocess failed (Executable: '%s', ExitCode: %s)" % (self.executable, exit_code)
                raise ProcessFailureException(exception_message, self.executable, exit_code)


    async def terminate(self, reason: str, exit_code: Optional[int] = None) -> None:
        async with self._termination_lock:
            await self._terminate_unsafe(reason, exit_code)


    async def _terminate_unsafe(self, reason: str, exit_code: Optional[int] = None) -> None:
        if not self._process.is_running:
            logger.debug("Requested subprocess termination but has already exited (Executable: '%s', PID: %s, Reason: '%s')", self.executable, self.pid, reason)
            return

        logger.warning("Terminating subprocess (Executable: '%s', PID: %s, Reason: '%s')", self.executable, self.pid, reason)

        if exit_code is not None:
            self._custom_exit_code = exit_code

        if self._process.is_running:
            logger.warning("Requesting subprocess termination (Executable: '%s', PID: %s)", self.executable, self.pid)
            self._process.terminate()

            try:
                await asyncio.wait_for(self._process.wait(), self._options.termination_timeout.total_seconds())
            except asyncio.TimeoutError:
                pass

        if self._process.is_running:
            logger.error("Forcing subprocess termination (Executable: '%s', PID: %s)", self.executable, self.pid)
            self._process.kill()

            try:
                await asyncio.wait_for(self._process.wait(), self._options.termination_timeout.total_seconds())
            except asyncio.TimeoutError:
                pass

        if self._timeout_task is not None:
            self._timeout_task.cancel()

        await self._wait_tasks()

        if self._process.is_running:
            logger.error("Terminating subprocess failed (Executable: '%s', PID: %s)", self.executable, self.pid)

        if not self._process.is_running:
            logger.warning("Terminating subprocess succeeded (Executable: '%s', PID: %s)", self.executable, self.pid)


    def add_output_handler(self, handler: ProcessOutputHandler) -> None:
        self._output_handlers.append(handler)


    def remove_output_handler(self, handler: ProcessOutputHandler) -> None:
        self._output_handlers.remove(handler)


    async def _watch_stdout(self, stream: asyncio.StreamReader) -> None:
        while True:
            line_as_bytes = await stream.readline()
            if not line_as_bytes:
                for handler in self._output_handlers:
                    handler.process_stdout_end()
                break

            self._last_output_time = time.time()
            line = line_as_bytes.decode(self._options.encoding)

            for handler in self._output_handlers:
                handler.process_stdout_line(line)


    async def _watch_stderr(self, stream: asyncio.StreamReader) -> None:
        while True:
            line_as_bytes = await stream.readline()
            if not line_as_bytes:
                for handler in self._output_handlers:
                    handler.process_stderr_end()
                break

            self._last_output_time = time.time()
            line = line_as_bytes.decode(self._options.encoding)

            for handler in self._output_handlers:
                handler.process_stderr_line(line)


    async def _watch_timeout(self) -> None:
        while self._process.is_running:
            try:
                self._check_timeouts()
            except TimeoutError:
                asyncio.create_task(self.terminate("TimeoutError"))
                break

            await asyncio.sleep(self._options.wait_update_interval.total_seconds())


    def _check_timeouts(self) -> None:

        def check(start: float, timeout: datetime.timedelta, reason: str) -> None:
            elapsed = datetime.timedelta(time.time() - start)

            if elapsed > timeout:
                exception_message = "Subprocess timed out with reason %s" % reason
                exception_message += " (Executable: '%s', PID: %s, Timeout: %s > %s)" % (self.executable, self.pid, elapsed, timeout)
                raise TimeoutError(exception_message)

        if self._options.run_timeout is not None and self._start_time is not None:
            check(self._start_time, self._options.run_timeout, "total runtime")
        if self._options.output_timeout is not None and self._last_output_time is not None:
            check(self._last_output_time, self._options.output_timeout, "no output")


    async def _wait_tasks(self) -> None:

        async def _check_task(identifier: str, task: asyncio.Task) -> None:
            try:
                await asyncio.wait_for(task, 1)
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                logger.warning("Task for %s timed out (Executable: '%s', PID: %s)", identifier, self.executable, self.pid)
            except Exception: # pylint: disable = broad-except
                logger.error("Task for %s raised an unhandled exception (Executable: '%s', PID: %s)", identifier, self.executable, self.pid, exc_info = True)

        tasks_to_wait = []
        if self._timeout_task is not None:
            tasks_to_wait.append(self._timeout_task)
        if self._stdout_task is not None:
            tasks_to_wait.append(self._stdout_task)
        if self._stderr_task is not None:
            tasks_to_wait.append(self._stderr_task)

        if len(tasks_to_wait) == 0:
            return

        await asyncio.wait(tasks_to_wait, timeout = 10, return_when = asyncio.ALL_COMPLETED)

        if self._timeout_task is not None:
            await _check_task("timeout", self._timeout_task)
        if self._stdout_task is not None:
            await _check_task("stdout", self._stdout_task)
        if self._stderr_task is not None:
            await _check_task("stderr", self._stderr_task)
