""" Integration tests for PythonPackageBuilder """

import os
import sys

import pytest

from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner
from bhamon_development_toolkit.python.python_package import PythonPackage
from bhamon_development_toolkit.python.python_package_builder import PythonPackageBuilder


@pytest.mark.asyncio
async def test_build_distribution_package(tmpdir):
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    builder = PythonPackageBuilder(sys.executable, process_runner)

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    output_directory = os.path.join(tmpdir, "output")

    os.makedirs(python_package.path_to_sources)
    if python_package.path_to_tests is not None:
        os.makedirs(python_package.path_to_tests)

    with open(os.path.join(python_package.path_to_sources, "pyproject.toml"), mode = "w", encoding = "utf-8") as pyproject_file:
        pyproject_file.write("[project]\n")
        pyproject_file.write("name = \"my-test-package\"\n")
        pyproject_file.write("version = \"1.0\"\n")

    await builder.build_distribution_package(python_package, output_directory, simulate = False)

    assert os.path.exists(os.path.join(output_directory, builder.get_distribution_package_file_name(python_package, "1.0")))


@pytest.mark.asyncio
async def test_build_distribution_package_with_simulate(tmpdir):
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    builder = PythonPackageBuilder(sys.executable, process_runner)

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    output_directory = os.path.join(tmpdir, "output")

    await builder.build_distribution_package(python_package, output_directory, simulate = True)
