""" Integration tests for python_helpers """

import os

import pytest

from bhamon_development_toolkit.python import python_helpers


def test_setup_virtual_environment(tmpdir):
    system_python_executable = python_helpers.resolve_system_python_executable()
    working_directory = os.path.join(tmpdir, "Working")
    venv_directory = os.path.join(working_directory, ".venv")
    venv_python_executable = python_helpers.get_venv_python_executable(venv_directory)

    python_helpers.setup_virtual_environment(system_python_executable, venv_directory)

    assert os.path.exists(venv_directory)
    assert os.path.exists(venv_python_executable)


def test_install_python_packages(tmpdir):
    system_python_executable = python_helpers.resolve_system_python_executable()
    working_directory = os.path.join(tmpdir, "Working")
    venv_directory = os.path.join(working_directory, ".venv")
    venv_python_executable = python_helpers.get_venv_python_executable(venv_directory)

    python_helpers.setup_virtual_environment(system_python_executable, venv_directory)

    python_helpers.install_python_packages(venv_python_executable, [ "pip" ])
    with pytest.raises(RuntimeError):
        python_helpers.install_python_packages(venv_python_executable, [ "does-not-exist" ])


def test_install_python_packages_for_development(tmpdir):
    system_python_executable = python_helpers.resolve_system_python_executable()
    working_directory = os.path.join(tmpdir, "Working")
    venv_directory = os.path.join(working_directory, ".venv")
    venv_python_executable = python_helpers.get_venv_python_executable(venv_directory)
    local_package_path = os.path.join(working_directory, "Sources", "my_package")

    python_helpers.setup_virtual_environment(system_python_executable, venv_directory)

    with pytest.raises(RuntimeError):
        python_helpers.install_python_packages_for_development(venv_python_executable, [ local_package_path ])

    os.makedirs(local_package_path)
    with open(os.path.join(local_package_path, "pyproject.toml"), mode = "w", encoding = "utf-8") as pyproject_file:
        pyproject_file.write("[project]\n")
        pyproject_file.write("name = \"my-local-package\"\n")
        pyproject_file.write("version = \"1.0\"\n")

    python_helpers.install_python_packages_for_development(venv_python_executable, [ local_package_path ])

    assert os.path.exists(os.path.join(local_package_path, "my_local_package.egg-info"))
