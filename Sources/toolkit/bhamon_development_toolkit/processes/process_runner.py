from typing import List, Optional

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner
from bhamon_development_toolkit.processes.process_status import ProcessStatus


class ProcessRunner:


    def __init__(self, spawner: ProcessSpawner) -> None:
        self._spawner = spawner


    async def run(self,
            command: ExecutableCommand,
            options: ProcessOptions,
            output_handlers: Optional[List[ProcessOutputHandler]] = None,
            check_exit_code: bool = True
            ) -> ProcessStatus:

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

        return watcher.get_status()
