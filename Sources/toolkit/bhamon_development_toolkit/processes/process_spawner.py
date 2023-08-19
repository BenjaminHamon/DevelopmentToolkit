import asyncio
import logging
import os
import platform
import signal
import subprocess

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.exceptions.process_start_exception import ProcessStartException
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_watcher import ProcessWatcher
from bhamon_development_toolkit.processes.process_wrapper import ProcessWrapper


logger = logging.getLogger("ProcessSpawner")


class ProcessSpawner:


    def __init__(self, is_console: bool = False) -> None:
        self.termination_signal: signal.Signals = signal.SIGTERM
        self.subprocess_flags: int = 0

        if platform.system() == "Windows":
            if is_console:
                self.termination_signal = signal.CTRL_BREAK_EVENT # pylint: disable = no-member
            self.subprocess_flags = subprocess.CREATE_NEW_PROCESS_GROUP # pylint: disable = no-member


    async def spawn_process(self, command: ExecutableCommand, options: ProcessOptions) -> ProcessWatcher:
        process_environment = os.environ.copy()
        process_environment["PYTHONIOENCODING"] = options.encoding # Force encoding instead of the default stdout encoding

        if options.environment is not None:
            process_environment.update(options.environment)

        try:
            process = await asyncio.create_subprocess_exec(*command.get_command(),
                stdin = subprocess.DEVNULL, stdout = subprocess.PIPE, stderr = subprocess.STDOUT,
                cwd = options.working_directory, env = process_environment, creationflags = self.subprocess_flags)

        except FileNotFoundError as exception:
            exception_message = "Executable not found: '%s'" % (command.executable_name)
            raise ProcessStartException(exception_message, command.executable_path, None) from exception

        logger.debug("Subprocess spawned (Executable: '%s', PID: %s)", command.executable_name, process.pid)

        process_wrapper = ProcessWrapper(process, self.termination_signal)
        process_watcher = ProcessWatcher(process_wrapper, command, options)

        return process_watcher
