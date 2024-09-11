""" Unit tests for PythonPackageBuilder """

import os
from typing import Any

import mockito
import pytest

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_result import ProcessResult
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.python.python_package import PythonPackage
from bhamon_development_toolkit.python.python_package_builder import PythonPackageBuilder


async def mock_future(result: Any) -> Any:
    return result


@pytest.mark.asyncio
async def test_build_distribution_package(tmpdir):
    process_runner = mockito.mock(spec = ProcessRunner)
    builder = PythonPackageBuilder("FakePython", process_runner) # type: ignore

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    output_directory = os.path.join(tmpdir, "output")

    mockito.when(process_runner).run(mockito.any(ExecutableCommand), mockito.any(ProcessOptions), mockito.any(list), check_exit_code = True) \
        .thenReturn(mock_future(ProcessResult(executable = "FakePython", exit_code = 0)))

    await builder.build_distribution_package(python_package, output_directory, simulate = False)


@pytest.mark.asyncio
async def test_build_distribution_package_with_simulate(tmpdir):
    process_runner = mockito.mock(spec = ProcessRunner)
    builder = PythonPackageBuilder("FakePython", process_runner) # type: ignore

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    output_directory = os.path.join(tmpdir, "output")

    await builder.build_distribution_package(python_package, output_directory, simulate = True)
