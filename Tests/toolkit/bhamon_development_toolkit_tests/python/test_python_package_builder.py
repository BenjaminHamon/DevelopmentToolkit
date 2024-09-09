""" Unit tests for PythonPackageBuilder """

import os

import mockito
import pytest

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.python.python_package import PythonPackage
from bhamon_development_toolkit.python.python_package_builder import PythonPackageBuilder


@pytest.mark.asyncio
async def test_build_distribution_package(tmpdir):

    async def run_as_mock() -> None:
        return None

    process_runner = mockito.mock(spec = ProcessRunner)
    builder = PythonPackageBuilder("FakePython", process_runner) # type: ignore

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    output_directory = os.path.join(tmpdir, "output")

    mockito.when(process_runner).run(mockito.any(ExecutableCommand), mockito.any(ProcessOptions), mockito.any(list)).thenReturn(run_as_mock())

    await builder.build_distribution_package(python_package, output_directory, simulate = False)


@pytest.mark.asyncio
async def test_build_distribution_package_with_simulate(tmpdir):
    process_runner = mockito.mock(spec = ProcessRunner)
    builder = PythonPackageBuilder("FakePython", process_runner) # type: ignore

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    output_directory = os.path.join(tmpdir, "output")

    await builder.build_distribution_package(python_package, output_directory, simulate = True)
