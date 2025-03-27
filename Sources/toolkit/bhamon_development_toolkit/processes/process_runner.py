from typing import List, Optional

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_collector import ProcessOutputCollector
from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler
from bhamon_development_toolkit.processes.process_result import ProcessResult
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner


class ProcessRunner:


    def __init__(self, spawner: ProcessSpawner) -> None:
        self._spawner = spawner


    async def run(self,
            command: ExecutableCommand,
            options: ProcessOptions,
            *,
            output_handlers: Optional[List[ProcessOutputHandler]] = None,
            check_exit_code: bool = True
        ) -> ProcessResult:

        watcher = await self._spawner.spawn_process(command = command, options = options)

        if output_handlers is not None:
            for handler in output_handlers:
                watcher.add_output_handler(handler)

        try:
            await watcher.start()
            await watcher.wait()
            await watcher.complete(check_exit_code)

        except BaseException as exception:
            if watcher.get_status().is_running:
                await watcher.terminate(type(exception).__name__)

            raise

        status = watcher.get_status()
        if status.exit_code is None:
            raise ValueError("Process exit code is not set")

        return ProcessResult(
            executable = status.executable,
            exit_code = status.exit_code,
        )


    async def run_with_collector(self,
            command: ExecutableCommand,
            options: ProcessOptions,
            *,
            check_exit_code: bool = True,
        ) -> ProcessResult:

        output_collector = ProcessOutputCollector()

        result = await self.run(command, options, output_handlers = [ output_collector ], check_exit_code = check_exit_code)

        return ProcessResult(
            executable = result.executable,
            exit_code = result.exit_code,
            standard_output = output_collector.get_stdout(),
            error_output = output_collector.get_stderr(),
        )
