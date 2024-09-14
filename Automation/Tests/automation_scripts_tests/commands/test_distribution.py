import argparse
import os

import mockito
import pytest

from bhamon_development_toolkit.automation import automation_helpers
from bhamon_development_toolkit.python.python_package import PythonPackage
from bhamon_development_toolkit.python.python_package_metadata import PythonPackageMetadata

from automation_scripts.commands.distribution import _PackageCommand
from automation_scripts.commands.distribution import _SetupCommand
from automation_scripts.configuration.project_configuration import ProjectConfiguration


@pytest.mark.asyncio
async def test_run_setup(tmpdir):
    with automation_helpers.execute_in_workspace(tmpdir):
        project_configuration = mockito.mock(spec = ProjectConfiguration)

        python_package = PythonPackage(
            identifier = "my-python-package",
            path_to_sources = os.path.join("Sources"),
            path_to_tests = os.path.join("Tests"))

        command = _SetupCommand()
        arguments = argparse.Namespace()

        mockito.when(project_configuration).get_python_package_metadata().thenReturn(PythonPackageMetadata())
        mockito.when(project_configuration).list_python_packages().thenReturn([ python_package ])

        metadata_file_path = os.path.join(python_package.path_to_sources, python_package.name_for_file_system, "__metadata__.py")

        assert not os.path.exists(metadata_file_path)

        os.makedirs(os.path.join("Sources", python_package.name_for_file_system))
        await command.run_async(arguments, configuration = project_configuration, simulate = False)

        assert os.path.exists(metadata_file_path)


@pytest.mark.asyncio
async def test_run_setup_with_simulate(tmpdir):
    with automation_helpers.execute_in_workspace(tmpdir):
        project_configuration = mockito.mock(spec = ProjectConfiguration)

        python_package = PythonPackage(
            identifier = "my-python-package",
            path_to_sources = os.path.join("Sources"),
            path_to_tests = os.path.join("Tests"))

        command = _SetupCommand()
        arguments = argparse.Namespace()

        mockito.when(project_configuration).get_python_package_metadata().thenReturn(PythonPackageMetadata())
        mockito.when(project_configuration).list_python_packages().thenReturn([ python_package ])

        metadata_file_path = os.path.join(python_package.path_to_sources, python_package.name_for_file_system, "__metadata__.py")

        assert not os.path.exists(metadata_file_path)

        os.makedirs(os.path.join("Sources", python_package.name_for_file_system))
        await command.run_async(arguments, configuration = project_configuration, simulate = True)

        assert not os.path.exists(metadata_file_path)


@pytest.mark.asyncio
async def test_run_package(tmpdir):
    with automation_helpers.execute_in_workspace(tmpdir):
        project_configuration = mockito.mock(spec = ProjectConfiguration)

        python_package = PythonPackage(
            identifier = "my-python-package",
            path_to_sources = os.path.join("Sources"),
            path_to_tests = os.path.join("Tests"))

        command = _PackageCommand()
        arguments = argparse.Namespace()

        mockito.when(project_configuration).list_python_packages().thenReturn([ python_package ])

        await command.run_async(arguments, configuration = project_configuration, simulate = False)
