import logging
import os
import platform
import shutil
import sys
from typing import List, Optional

from bhamon_development_toolkit.processes import process_helpers
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand


logger = logging.getLogger("Python")


class PythonEnvironment:


    def __init__(self, system_python_executable: str, venv_directory: str) -> None:
        self._system_python_executable = system_python_executable
        self._venv_directory = venv_directory


    def get_venv_directory(self) -> str:
        return self._venv_directory


    def get_venv_python_executable(self) -> str:
        return self.get_venv_executable("python")


    def get_venv_executable(self, executable: str) -> str:
        if platform.system() == "Windows":
            return os.path.join(self._venv_directory, "scripts", executable + ".exe")
        return os.path.join(self._venv_directory, "bin", executable)


    def _get_pip_configuration_file_path(self) -> str:
        if platform.system() == "Windows":
            return os.path.join(self._venv_directory, "pip.ini")
        return os.path.join(self._venv_directory, "pip.conf")


    def setup_virtual_environment(self, pip_configuration_file_path: Optional[str] = None, simulate: bool = False) -> None:
        venv_python_executable = self.get_venv_python_executable()
        if sys.executable.lower() == os.path.abspath(venv_python_executable).lower():
            raise RuntimeError("Active python is the target virtual environment")

        if os.path.isdir(self._venv_directory) and not simulate:
            # Try to remove the executable first since it might be in use, otherwise we would be leaving a broken venv
            if platform.system() == "Windows" and os.path.exists(os.path.join(self._venv_directory, "scripts", "python.exe")):
                os.remove(os.path.join(self._venv_directory, "scripts", "python.exe"))
            shutil.rmtree(self._venv_directory)

        venv_command = ExecutableCommand(self._system_python_executable)
        venv_command.add_arguments([ "-m", "venv", self._venv_directory ])

        process_helpers.run_simple(logger, venv_command, simulate = simulate)

        if pip_configuration_file_path is not None:
            pip_configuration_file_path_in_venv = self._get_pip_configuration_file_path()
            if not simulate:
                shutil.copy(pip_configuration_file_path, pip_configuration_file_path_in_venv)

        self.install_python_packages([ "pip", "wheel" ], simulate = simulate)


    def install_python_packages(self,
            name_or_path_collection: List[str], simulate: bool = False) -> None:

        install_command = ExecutableCommand(self.get_venv_python_executable())
        install_command.add_arguments([ "-m", "pip", "install", "--upgrade" ] + name_or_path_collection)

        process_helpers.run_simple(logger, install_command, simulate = simulate)


    def install_python_packages_for_development(self,
            name_or_path_collection: List[str], simulate: bool = False) -> None:

        def is_local_package(name_or_path: str) -> bool:
            return name_or_path.startswith(".") or "/" in name_or_path or "\\" in name_or_path

        install_command = ExecutableCommand(self.get_venv_python_executable())
        install_command.add_arguments([ "-m", "pip", "install", "--upgrade" ])

        for name_or_path in name_or_path_collection:
            install_command.add_arguments([ "--editable", name_or_path ] if is_local_package(name_or_path) else [ name_or_path ])

        process_helpers.run_simple(logger, install_command, simulate = simulate)
