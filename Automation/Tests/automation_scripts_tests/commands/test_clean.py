import argparse
import os

import mockito
import pytest

from bhamon_development_toolkit.automation import automation_helpers
from bhamon_development_toolkit.python.python_package import PythonPackage

from automation_scripts.commands.clean import CleanCommand
from automation_scripts.configuration.project_configuration import ProjectConfiguration


@pytest.mark.asyncio
async def test_run(tmpdir):
    with automation_helpers.execute_in_workspace(tmpdir):
        os.makedirs(os.path.join("Sources", "some_module", "__pycache__"))

        project_configuration = mockito.mock(spec = ProjectConfiguration)

        automation_package = PythonPackage(
            identifier = "my-automation-package",
            path_to_sources = os.path.join("Automation", "Scripts"),
            path_to_tests = os.path.join("Automation", "Tests"))

        python_package = PythonPackage(
            identifier = "my-python-package",
            path_to_sources = os.path.join("Sources"),
            path_to_tests = os.path.join("Tests"))

        command = CleanCommand()
        arguments = argparse.Namespace()

        mockito.when(project_configuration).list_automation_packages().thenReturn([ automation_package ])
        mockito.when(project_configuration).list_python_packages().thenReturn([ python_package ])

        assert os.path.exists(os.path.join("Sources", "some_module", "__pycache__"))

        await command.run_async(arguments, configuration = project_configuration, simulate = False)

        assert not os.path.exists(os.path.join("Sources", "some_module", "__pycache__"))


@pytest.mark.asyncio
async def test_run_with_simulate(tmpdir):
    with automation_helpers.execute_in_workspace(tmpdir):
        os.makedirs(os.path.join("Sources", "some_module", "__pycache__"))

        project_configuration = mockito.mock(spec = ProjectConfiguration)

        automation_package = PythonPackage(
            identifier = "my-automation-package",
            path_to_sources = os.path.join("Automation", "Scripts"),
            path_to_tests = os.path.join("Automation", "Tests"))

        python_package = PythonPackage(
            identifier = "my-python-package",
            path_to_sources = os.path.join("Sources"),
            path_to_tests = os.path.join("Tests"))

        command = CleanCommand()
        arguments = argparse.Namespace()

        mockito.when(project_configuration).list_automation_packages().thenReturn([ automation_package ])
        mockito.when(project_configuration).list_python_packages().thenReturn([ python_package ])

        assert os.path.exists(os.path.join("Sources", "some_module", "__pycache__"))

        await command.run_async(arguments, configuration = project_configuration, simulate = True)

        assert os.path.exists(os.path.join("Sources", "some_module", "__pycache__"))
