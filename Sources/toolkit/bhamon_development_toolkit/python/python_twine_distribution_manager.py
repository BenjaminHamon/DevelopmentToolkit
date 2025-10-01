import logging
from typing import Optional

from benjaminhamon_standard_extensions.processes import process_helpers
from benjaminhamon_standard_extensions.processes.executable_command import ExecutableCommand


logger = logging.getLogger("Python")


class PythonTwineDistributionManager:


    def __init__(self, python_executable: str) -> None:
        self._python_executable = python_executable

        self.repository_url: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None


    def upload_package(self, package_path: str, *, simulate: bool = False) -> None:
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

        process_helpers.run_simple(logger, upload_command, simulate = simulate)
