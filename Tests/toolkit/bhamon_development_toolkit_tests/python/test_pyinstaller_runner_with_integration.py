# cspell:words filevers prodvers pyinstaller

""" Integration tests for PyInstallerRunner """

import os
import platform
import subprocess
import sys

import pytest

from benjaminhamon_standard_extensions.processes.process_runner import ProcessRunner
from benjaminhamon_standard_extensions.processes.process_spawner import ProcessSpawner

from bhamon_development_toolkit.python.pyinstaller_configuration import PyInstallerConfiguration
from bhamon_development_toolkit.python.pyinstaller_runner import PyInstallerRunner


@pytest.mark.asyncio
async def test_run(tmpdir):
    pyinstaller_executable = os.path.join(os.path.dirname(sys.executable), "pyinstaller")
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    pyinstaller_runner = PyInstallerRunner(process_runner, pyinstaller_executable)

    configuration = PyInstallerConfiguration(
        application_source_file_path = os.path.join(tmpdir, "Sources", "application.py"),
        executable_name = "TheApplication",
        single_file = True,
    )

    os.makedirs(os.path.join(tmpdir, "Sources"))
    with open(configuration.application_source_file_path, mode = "w", encoding = "utf-8") as source_file:
        source_file.write("print('hello')\n")

    output_directory = os.path.join(tmpdir, "Output")
    intermediate_directory = os.path.join(tmpdir, "Output-Intermediate")

    executable_path = os.path.join(output_directory, configuration.executable_name)
    if platform.system() == "Windows":
        executable_path += ".exe"

    assert not os.path.exists(executable_path)

    await pyinstaller_runner.run(configuration, output_directory, intermediate_directory)

    assert os.path.exists(executable_path)

    result = subprocess.run([ executable_path ], check = True, capture_output = True, text = True)

    assert result.stdout.strip() == "hello"
