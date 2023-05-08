import argparse
import os

import mockito
import pytest

from bhamon_development_toolkit.automation import automation_helpers
from bhamon_development_toolkit.python.python_package import PythonPackage

from automation_scripts.commands.lint import LintCommand
from automation_scripts.configuration.project_configuration import ProjectConfiguration


@pytest.mark.asyncio
async def test_run_with_success(tmpdir):
    with automation_helpers.execute_in_workspace(tmpdir):
        project_configuration = mockito.mock(spec = ProjectConfiguration)
        python_package = mockito.mock(spec = PythonPackage)
        python_package.identifier = "my-python-package" # type: ignore
        python_package.path_to_sources = "Sources" # type: ignore
        python_package.name_for_module_import = "Sources" # type: ignore

        command = LintCommand()
        arguments = argparse.Namespace(run_identifier = "my-run-identifier")

        os.makedirs(python_package.path_to_sources)
        with open(os.path.join(python_package.path_to_sources, "my_module.py"), mode = "w", encoding = "utf-8") as source_file:
            source_file.write("\"\"\"Sample module\"\"\"\n")

        mockito.when(project_configuration).list_python_packages().thenReturn([ python_package ])

        await command.run_async(arguments, configuration = project_configuration, simulate = False)


@pytest.mark.asyncio
async def test_run_with_failure(tmpdir):
    with automation_helpers.execute_in_workspace(tmpdir):
        project_configuration = mockito.mock(spec = ProjectConfiguration)
        python_package = mockito.mock(spec = PythonPackage)
        python_package.identifier = "my-python-package" # type: ignore
        python_package.path_to_sources = "Sources" # type: ignore
        python_package.name_for_module_import = "Sources" # type: ignore

        command = LintCommand()
        arguments = argparse.Namespace(run_identifier = "my-run-identifier")

        os.makedirs(python_package.path_to_sources)
        with open(os.path.join(python_package.path_to_sources, "my_module.py"), mode = "w", encoding = "utf-8") as source_file:
            source_file.write("def my_function():\n    do_nothing()\n")

        mockito.when(project_configuration).list_python_packages().thenReturn([ python_package ])

        with pytest.raises(RuntimeError):
            await command.run_async(arguments, configuration = project_configuration, simulate = False)


@pytest.mark.asyncio
async def test_run_with_simulate(tmpdir):
    with automation_helpers.execute_in_workspace(tmpdir):
        project_configuration = mockito.mock(spec = ProjectConfiguration)
        python_package = PythonPackage(identifier = "my-python-package", path_to_sources = "Sources", path_to_tests = "Tests")

        command = LintCommand()
        arguments = argparse.Namespace(run_identifier = "my-run-identifier")

        mockito.when(project_configuration).list_python_packages().thenReturn([ python_package ])

        await command.run_async(arguments, configuration = project_configuration, simulate = True)
