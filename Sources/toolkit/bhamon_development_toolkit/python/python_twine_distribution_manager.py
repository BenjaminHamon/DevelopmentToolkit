import logging
from typing import Optional

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.python import python_helpers


logger = logging.getLogger("Python")


class PythonTwineDistributionManager:


    def __init__(self, python_executable: str) -> None:
        self._python_executable = python_executable

        self.repository_url: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None


    def upload_package(self, package_path: str, simulate: bool = False) -> None:
        if self.username is None:
            raise ValueError("Username is required")
        if self.password is None:
            raise ValueError("Password is required")

        upload_command = ExecutableCommand(self._python_executable)
        upload_command.add_arguments([ "-m", "twine", "upload" ])
        upload_command.add_internal_arguments([ "--non-interactive", "--disable-progress-bar" ], [])

        if self.repository_url is not None:
            upload_command.add_arguments([ "--repository-url", self.repository_url ])

        upload_command.add_internal_arguments([ "--username", self.username ], [ "--username", "***" ])
        upload_command.add_internal_arguments([ "--password", self.password ], [ "--password", "***" ])

        upload_command.add_arguments([ package_path ])

        python_helpers.run_python_command(upload_command, simulate = simulate)
