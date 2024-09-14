import argparse
import os

import pytest

from bhamon_development_toolkit.automation import automation_helpers

from automation_scripts.commands.clean import CleanCommand


@pytest.mark.asyncio
async def test_run(workspace, automation_configuration):
    with automation_helpers.execute_in_workspace(workspace):
        python_package = automation_configuration.project_python_elements.package_collection[0]
        cache_directory = os.path.join(python_package.path_to_sources, python_package.name_for_file_system, "__pycache__")

        os.makedirs(cache_directory)

        command = CleanCommand()
        arguments = argparse.Namespace()

        assert os.path.exists(cache_directory)
        await command.run_async(arguments, configuration = automation_configuration, simulate = False)
        assert not os.path.exists(cache_directory)


@pytest.mark.asyncio
async def test_run_with_simulate(workspace, automation_configuration):
    with automation_helpers.execute_in_workspace(workspace):
        python_package = automation_configuration.project_python_elements.package_collection[0]
        cache_directory = os.path.join(python_package.path_to_sources, python_package.name_for_file_system, "__pycache__")

        os.makedirs(cache_directory)

        command = CleanCommand()
        arguments = argparse.Namespace()

        assert os.path.exists(cache_directory)
        await command.run_async(arguments, configuration = automation_configuration, simulate = True)
        assert os.path.exists(cache_directory)
