# cspell:words filevers prodvers pyinstaller

""" Unit tests for PyInstallerRunner """

import os
from typing import Any

import mockito
import pytest

from bhamon_development_toolkit.applications.application_metadata import ApplicationMetadata
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_result import ProcessResult
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.python.pyinstaller_configuration import PyInstallerConfiguration
from bhamon_development_toolkit.python.pyinstaller_runner import PyInstallerRunner


async def mock_future(result: Any) -> Any:
    return result


@pytest.mark.asyncio
async def test_run(tmpdir):
    process_runner = mockito.mock(spec = ProcessRunner)
    pyinstaller_runner = PyInstallerRunner(process_runner, "FakePyInstaller") # type: ignore

    configuration = PyInstallerConfiguration(
        application_source_file_path = os.path.join(tmpdir, "Sources", "application.py"),
        executable_name = "TheApplication",
        single_file = True,
    )

    output_directory = os.path.join(tmpdir, "Output")
    intermediate_directory = os.path.join(tmpdir, "Output-Intermediate")

    mockito.when(process_runner).run(mockito.any(ExecutableCommand), mockito.any(ProcessOptions), mockito.any(list), check_exit_code = True) \
        .thenReturn(mock_future(ProcessResult("FakePyInstaller", 0)))

    await pyinstaller_runner.run(configuration, output_directory, intermediate_directory)


@pytest.mark.asyncio
async def test_run_with_simulate(tmpdir):
    process_runner = mockito.mock(spec = ProcessRunner)
    pyinstaller_runner = PyInstallerRunner(process_runner, "FakePyInstaller") # type: ignore

    configuration = PyInstallerConfiguration(
        application_source_file_path = os.path.join(tmpdir, "Sources", "application.py"),
        executable_name = "TheApplication",
        single_file = True,
    )

    output_directory = os.path.join(tmpdir, "Output")
    intermediate_directory = os.path.join(tmpdir, "Output-Intermediate")

    await pyinstaller_runner.run(configuration, output_directory, intermediate_directory, simulate = True)


def test_generate_windows_version_info():
    process_runner = mockito.mock(spec = ProcessRunner)
    pyinstaller_runner = PyInstallerRunner(process_runner, "FakePyInstaller") # type: ignore

    application_metadata = ApplicationMetadata(
        product_identifier = "TheProductIdentifier",
        version_identifier = "1.2.3",
        version_identifier_full = "1.2.3+abcde",
        product_copyright = "Copyright (c) 2020 The Copyright Holder",
    )

    expected = """
VSVersionInfo(
    ffi = FixedFileInfo(
        filevers = (1, 2, 3, 0),
        prodvers = (1, 2, 3, 0),
    ),
    kids = [
        StringFileInfo([
            StringTable(
                "040904B0",
                [
                    StringStruct("ProductName", "TheProductIdentifier"),
                    StringStruct("ProductVersion", "1.2.3+abcde"),
                    StringStruct("FileVersion", "1.2.3"),
                    StringStruct("LegalCopyright", "Copyright (c) 2020 The Copyright Holder"),
                ])
        ]),
		VarFileInfo([VarStruct("Translation", [1033, 1200])])
    ]
)
"""

    expected = expected.lstrip()

    actual = pyinstaller_runner.generate_windows_version_info(application_metadata)

    assert actual == expected
