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

    async def fake_setup(python_package: PythonPackage) -> None:
        archive_name = python_package.name_for_file_system + "-" + python_package_version
        archive_path = os.path.join(python_package.path_to_sources, "dist", archive_name + "-py3-none-any.whl")

        os.makedirs(os.path.dirname(archive_path))
        with open(archive_path, mode = "wb"):
            pass

        return None

    process_runner = mockito.mock(spec = ProcessRunner)
    builder = PythonPackageBuilder("FakePython", process_runner) # type: ignore

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    python_package_version = "1.0"
    output_directory = os.path.join(tmpdir, "output")

    archive_name = python_package.name_for_file_system + "-" + python_package_version
    archive_path = os.path.join(output_directory, archive_name + "-py3-none-any.whl")

    os.makedirs(python_package.path_to_sources)
    if python_package.path_to_tests is not None:
        os.makedirs(python_package.path_to_tests)

    mockito.when(process_runner).run(mockito.any(ExecutableCommand), mockito.any(ProcessOptions), mockito.any(list)).thenReturn(fake_setup(python_package))

    await builder.build_distribution_package(python_package, python_package_version, output_directory, simulate = False)

    assert os.path.isfile(archive_path)


@pytest.mark.asyncio
async def test_build_distribution_package_with_simulate(tmpdir):
    process_runner = mockito.mock(spec = ProcessRunner)
    builder = PythonPackageBuilder("FakePython", process_runner) # type: ignore

    python_package = PythonPackage("my-test-package", "sources", "tests")
    python_package_version = "1.0"
    output_directory = os.path.join(tmpdir, "output")

    await builder.build_distribution_package(python_package, python_package_version, output_directory, simulate = True)
