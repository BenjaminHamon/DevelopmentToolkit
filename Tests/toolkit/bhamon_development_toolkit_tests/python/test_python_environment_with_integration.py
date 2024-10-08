""" Integration tests for PythonEnvironment """

import os

import pytest

from bhamon_development_toolkit.processes.exceptions.process_failure_exception import ProcessFailureException
from bhamon_development_toolkit.python import python_helpers
from bhamon_development_toolkit.python.python_environment import PythonEnvironment


@pytest.mark.asyncio
async def test_setup_virtual_environment(tmpdir):
    python_environment = PythonEnvironment(
        system_python_executable = python_helpers.resolve_system_python_executable(),
        venv_directory = os.path.join(tmpdir, "Working", ".venv"),
    )

    await python_environment.setup_virtual_environment()

    assert os.path.exists(python_environment.get_venv_directory())
    assert os.path.exists(python_environment.get_venv_python_executable())


@pytest.mark.asyncio
async def test_install_python_packages(tmpdir):
    python_environment = PythonEnvironment(
        system_python_executable = python_helpers.resolve_system_python_executable(),
        venv_directory = os.path.join(tmpdir, "Working", ".venv"),
    )

    await python_environment.setup_virtual_environment()

    await python_environment.install_python_packages([ "pip" ])
    with pytest.raises(ProcessFailureException):
        await python_environment.install_python_packages([ "does-not-exist" ])


@pytest.mark.asyncio
async def test_install_python_packages_for_development(tmpdir):
    python_environment = PythonEnvironment(
        system_python_executable = python_helpers.resolve_system_python_executable(),
        venv_directory = os.path.join(tmpdir, "Working", ".venv"),
    )

    local_package_path = os.path.join(tmpdir, "Working", "Sources", "my_package")

    await python_environment.setup_virtual_environment()

    with pytest.raises(ProcessFailureException):
        await python_environment.install_python_packages_for_development([ local_package_path ])

    os.makedirs(local_package_path)
    with open(os.path.join(local_package_path, "pyproject.toml"), mode = "w", encoding = "utf-8") as pyproject_file:
        pyproject_file.write("[project]\n")
        pyproject_file.write("name = \"my-local-package\"\n")
        pyproject_file.write("version = \"1.0\"\n")

    await python_environment.install_python_packages_for_development([ local_package_path ])

    assert os.path.exists(os.path.join(local_package_path, "my_local_package.egg-info"))
