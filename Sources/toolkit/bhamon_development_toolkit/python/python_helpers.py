import logging
import os
import platform
import shutil
import sys
from typing import List, Optional


logger = logging.getLogger("Python")


def resolve_system_python_executable() -> str:
    if hasattr(sys, "_base_executable"):
        return sys._base_executable # type: ignore # pylint: disable = protected-access
    raise RuntimeError("Unable to resolve the system Python executable")


def find_and_check_system_python_executable(python_versions: List[str]) -> str:
    python_executable = find_system_python_executable(python_versions)
    if python_executable is None or not shutil.which(python_executable):
        raise RuntimeError("Python3 is required (Path: %r)" % python_executable)

    return python_executable


def find_system_python_executable(python_versions: List[str]) -> Optional[str]:
    if platform.system() == "Linux":
        possible_paths = []

        for version in python_versions:
            possible_paths += [
                "/usr/bin/python" + version,
            ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

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
