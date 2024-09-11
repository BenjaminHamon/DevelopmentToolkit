""" Integration tests for PythonPackageBuilder """

import os
import sys

import pytest

from bhamon_development_toolkit.processes.exceptions.process_failure_exception import ProcessFailureException
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


@pytest.mark.asyncio
async def test_build_distribution_package_with_custom_settings(tmpdir):
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    builder = PythonPackageBuilder(sys.executable, process_runner)

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    output_directory = os.path.join(tmpdir, "output")

    os.makedirs(python_package.path_to_sources)
    if python_package.path_to_tests is not None:
        os.makedirs(python_package.path_to_tests)

    pyproject_data = """
[project]
name = "my-test-package"
version = "1.0+local"
"""

    pyproject_data = pyproject_data.lstrip()

    with open(os.path.join(python_package.path_to_sources, "pyproject.toml"), mode = "w", encoding = "utf-8") as pyproject_file:
        pyproject_file.write(pyproject_data)

    await builder.build_distribution_package_with_custom_settings(python_package, output_directory, { "version": "1.1" }, simulate = False)

    assert not os.path.exists(os.path.join(output_directory, builder.get_distribution_package_file_name(python_package, "1.0+local")))
    assert os.path.exists(os.path.join(output_directory, builder.get_distribution_package_file_name(python_package, "1.1")))

    with open(os.path.join(python_package.path_to_sources, "pyproject.toml"), mode = "r", encoding = "utf-8") as pyproject_file:
        assert pyproject_file.read() == pyproject_data


@pytest.mark.asyncio
async def test_build_distribution_package_with_custom_settings_with_exception(tmpdir):
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    builder = PythonPackageBuilder(sys.executable, process_runner)

    python_package = PythonPackage("my-test-package", os.path.join(tmpdir, "sources"), os.path.join(tmpdir, "tests"))
    output_directory = os.path.join(tmpdir, "output")

    os.makedirs(python_package.path_to_sources)
    if python_package.path_to_tests is not None:
        os.makedirs(python_package.path_to_tests)

    pyproject_data = """
[project]
name = "my-test-package"
version = "1.0+local"
"""

    pyproject_data = pyproject_data.lstrip()

    with open(os.path.join(python_package.path_to_sources, "pyproject.toml"), mode = "w", encoding = "utf-8") as pyproject_file:
        pyproject_file.write(pyproject_data)

    with pytest.raises(ProcessFailureException):
        await builder.build_distribution_package_with_custom_settings(python_package, output_directory, { "version": "invalid" }, simulate = False)

    assert not os.path.exists(os.path.join(output_directory, builder.get_distribution_package_file_name(python_package, "1.0+local")))
    assert not os.path.exists(os.path.join(output_directory, builder.get_distribution_package_file_name(python_package, "invalid")))

    with open(os.path.join(python_package.path_to_sources, "pyproject.toml"), mode = "r", encoding = "utf-8") as pyproject_file:
        assert pyproject_file.read() == pyproject_data
