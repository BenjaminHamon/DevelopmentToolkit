import logging
import os
from typing import Dict, List, Optional, Union

from bhamon_development_toolkit.processes import process_helpers
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_result import ProcessResult
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner


logger = logging.getLogger("Git")


class GitDirectClient:
    """ Client for git which maps its functions directly. """


    def __init__(self, process_spawner: ProcessSpawner, git_executable: Optional[str] = None, working_directory: Optional[str] = None) -> None:
        self._process_spawner = process_spawner
        self._git_executable = git_executable if git_executable is not None else "git"
        self.working_directory = working_directory if working_directory is not None else os.getcwd()
        self.encoding: str = "utf-8"
        self.configuration_options: Dict[str,Union[bool,int,str]] = {}


    def create_command(self) -> ExecutableCommand:

        def format_configuration_value(value: Union[bool,int,str]) -> str:
            if isinstance(value, bool):
                return str(value).lower()
            return str(value)

        command = ExecutableCommand(self._git_executable)
        for key, value in self.configuration_options.items():
            command.add_arguments([ "-c", "%s=%s" % (key, format_configuration_value(value)) ])

        return command


    async def execute_command(self, command: ExecutableCommand) -> ProcessResult:
        process_options = ProcessOptions(working_directory = self.working_directory)

        logger.debug("+ %s", process_helpers.format_executable_command(command.get_command_for_logging()))

        return await process_helpers.run_with_collector(self._process_spawner, command, process_options, check_exit_code = False)


    async def branch(self, show_current: bool = False) -> ProcessResult:
        """ List, create, or delete branches. """

        command = self.create_command()

        command.add_arguments([ "branch" ])
        if show_current:
            command.add_arguments([ "--show-current" ])

        return await self.execute_command(command)


    async def commit(self, message: Optional[str], allow_empty: bool = False, no_edit: bool = False) -> ProcessResult:
        """ Record changes to the repository. """

        command = self.create_command()

        command.add_arguments([ "commit" ])
        if message is not None:
            command.add_arguments([ "--message", message ])
        if allow_empty:
            command.add_arguments([ "--allow-empty" ])
        if no_edit:
            command.add_arguments([ "--no-edit" ])

        return await self.execute_command(command)


    async def init(self) -> ProcessResult:
        """ Create an empty Git repository or reinitialize an existing one. """

        command = self.create_command()

        command.add_arguments([ "init" ])

        return await self.execute_command(command)


    async def rev_list(self, commits: List[str], max_count: Optional[int] = None) -> ProcessResult:
        """ Lists commit objects in reverse chronological order. """

        command = self.create_command()

        command.add_arguments([ "rev-list" ])
        if max_count is not None:
            command.add_arguments([ "--max-count", str(max_count) ])
        command.add_arguments(commits)

        return await self.execute_command(command)


    async def show(self, objects: Optional[List[str]] = None, _format: Optional[str] = None, no_patch: bool = False) -> ProcessResult:
        """ Show various types of objects. """

        command = self.create_command()

        command.add_arguments([ "show" ])
        if _format is not None:
            command.add_arguments([ "--format=" + _format ])
        if no_patch:
            command.add_arguments([ "--no-patch" ])
        if objects is not None:
            command.add_arguments(objects)

        return await self.execute_command(command)
