import logging
import os
import subprocess
from typing import Dict, List, Optional, Union

from bhamon_development_toolkit.processes.process_result import ProcessResult


logger = logging.getLogger("Git")


class GitDirectClient:
    """ Client for git which maps its functions directly. """


    def __init__(self, git_executable: Optional[str] = None, working_directory: Optional[str] = None) -> None:
        self._git_executable = git_executable if git_executable is not None else "git"
        self.working_directory = working_directory if working_directory is not None else os.getcwd()
        self.encoding: str = "utf-8"
        self.configuration_options: Dict[str,Union[bool,int,str]] = {}


    def execute_command(self, command: List[str]) -> ProcessResult:

        def format_configuration_value(value: Union[bool,int,str]) -> str:
            if isinstance(value, bool):
                return str(value).lower()
            if isinstance(value, int):
                return str(value)
            if isinstance(value, str):
                return repr(value)

            raise ValueError("Unexpected type: '%s'" % type(value))

        full_command = [ self._git_executable ]
        for key, value in self.configuration_options.items():
            full_command += [ "-c", "%s=%s" % (key, format_configuration_value(value)) ]
        full_command += command

        command_result = subprocess.run(full_command,
            check = False, stdin = subprocess.DEVNULL, capture_output = True, text = True, encoding = self.encoding, cwd = self.working_directory)

        return ProcessResult.create_from_completed_process(command_result)


    def branch(self, show_current: bool = False) -> ProcessResult:
        """ List, create, or delete branches. """

        command = [ "branch" ]
        command += [ "--show-current" ] if show_current else []

        return self.execute_command(command)


    def commit(self, message: Optional[str], allow_empty: bool = False, no_edit: bool = False) -> ProcessResult:
        """ Record changes to the repository. """

        command = [ "commit" ]
        command += [ "--message", message ] if message is not None else []
        command += [ "--allow-empty" ] if allow_empty else []
        command += [ "--no-edit" ] if no_edit else []

        return self.execute_command(command)


    def init(self) -> ProcessResult:
        """ Create an empty Git repository or reinitialize an existing one. """

        command = [ "init" ]

        return self.execute_command(command)


    def rev_list(self, commits: List[str], max_count: Optional[int] = None) -> ProcessResult:
        """ Lists commit objects in reverse chronological order. """

        command = [ "rev-list" ]
        command += [ "--max-count", str(max_count) ] if max_count is not None else []
        command += commits

        return self.execute_command(command)


    def show(self, objects: Optional[List[str]] = None, _format: Optional[str] = None, no_patch: bool = False) -> ProcessResult:
        """ Show various types of objects. """

        command = [ "show" ]
        command += [ "--format=" + _format ] if _format is not None else []
        command += [ "--no-patch" ] if no_patch else []
        command += objects if objects is not None else []

        return self.execute_command(command)
