import logging
import os
import platform
import shutil
import subprocess
import sys
from typing import List, Optional

from bhamon_development_toolkit.processes import process_helpers
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand


logger = logging.getLogger("Python")


def find_and_check_system_python_executable(python_versions: List[str]) -> str:
    python_executable = find_system_python_executable(python_versions)
    if python_executable is None or not shutil.which(python_executable):
        raise RuntimeError("Python3 is required (Path: %r)" % python_executable)

    return python_executable


def find_system_python_executable(python_versions: List[str]) -> Optional[str]:
    if platform.system() == "Linux":
        return "/usr/bin/python3"

    if platform.system() == "Windows":
        possible_paths = []

        for version in python_versions:
            possible_paths += [
                os.path.join(os.environ["SystemDrive"] + "\\", "Python%s" % version.replace(".", ""), "python.exe"),
                os.path.join(os.environ["ProgramFiles"], "Python%s" % version.replace(".", ""), "python.exe"),
            ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    raise ValueError("Unsupported platform: '%s'" % platform.system())


def setup_virtual_environment(python_system_executable: str, venv_directory: str, simulate: bool) -> None:
    logger.info("Setting up python virtual environment (Path: %s)", venv_directory)

    venv_python_executable = get_venv_python_executable(venv_directory)
    if sys.executable.lower() == os.path.abspath(venv_python_executable).lower():
        raise RuntimeError("Active python is the target virtual environment")

    if os.path.isdir(venv_directory) and not simulate:
        # Try to remove the executable first since it might be in use, otherwise we would be leaving a broken venv
        if platform.system() == "Windows" and os.path.exists(os.path.join(venv_directory, "scripts", "python.exe")):
            os.remove(os.path.join(venv_directory, "scripts", "python.exe"))
        shutil.rmtree(venv_directory)

    venv_command = ExecutableCommand(python_system_executable)
    venv_command.add_arguments([ "-m", "venv", venv_directory ])

    run_python_command(venv_command, simulate = simulate)

    if platform.system() in [ "Darwin", "Linux" ] and not os.path.exists(os.path.join(venv_directory, "scripts")) and not simulate:
        os.symlink("bin", os.path.join(venv_directory, "scripts"))

    install_python_packages(venv_python_executable, [ "pip", "wheel" ], simulate = simulate)


def get_venv_python_executable(venv_directory: str) -> str:
    if platform.system() == "Windows":
        return os.path.join(venv_directory, "scripts", "python.exe")
    return os.path.join(venv_directory, "bin", "python")


def install_python_packages(python_executable: str,
        name_or_path_collection: List[str], python_package_repository: Optional[str] = None, simulate: bool = False) -> None:

    def is_local_package(name_or_path: str) -> bool:
        return name_or_path.startswith(".") or "/" in name_or_path or "\\" in name_or_path

    install_command = ExecutableCommand(python_executable)
    install_command.add_arguments([ "-m", "pip", "install", "--upgrade" ])

    if python_package_repository is not None:
        install_command.add_arguments([ "--extra-index", python_package_repository ])

    for name_or_path in name_or_path_collection:
        install_command.add_arguments([ "--editable", name_or_path ] if is_local_package(name_or_path) else [ name_or_path ])

    run_python_command(install_command, simulate = simulate)


def run_python_command(command: ExecutableCommand, working_directory: Optional[str] = None, simulate: bool = False) -> None:
    logger.info("+ %s", process_helpers.format_executable_command(command.get_command_for_logging()))

    subprocess_options = {
        "cwd": working_directory,
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "stdin": subprocess.DEVNULL,
    }

    if not simulate:
        process_result = subprocess.run(command.get_command(), check = False, **subprocess_options)
        for line in process_result.stdout.splitlines():
            logger.debug(line)
        for line in process_result.stderr.splitlines():
            logger.error(line)

        if process_result.returncode != 0:
            raise RuntimeError("Python command failed (ExitCode: %r)" % process_result.returncode)
