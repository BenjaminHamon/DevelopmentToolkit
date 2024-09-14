import argparse

import pytest

from bhamon_development_toolkit.automation import automation_helpers

from automation_scripts.commands.info import InfoCommand


@pytest.mark.asyncio
async def test_run(workspace, automation_configuration):
    with automation_helpers.execute_in_workspace(workspace):
        command = InfoCommand()

        await command.run_async(argparse.Namespace(), configuration = automation_configuration, simulate = False)


@pytest.mark.asyncio
async def test_run_with_simulate(workspace, automation_configuration):
    with automation_helpers.execute_in_workspace(workspace):
        command = InfoCommand()

        await command.run_async(argparse.Namespace(), configuration = automation_configuration, simulate = True)
