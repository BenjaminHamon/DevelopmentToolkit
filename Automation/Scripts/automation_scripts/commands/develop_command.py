import argparse
import logging
from typing import List

from bhamon_development_toolkit.automation.automation_command import AutomationCommand
from bhamon_development_toolkit.python import python_helpers
from bhamon_development_toolkit.python.python_environment import PythonEnvironment

from automation_scripts.configuration.automation_configuration import AutomationConfiguration


logger = logging.getLogger("Main")


class DevelopCommand(AutomationCommand):


    def configure_argument_parser(self, subparsers: argparse._SubParsersAction, **kwargs) -> argparse.ArgumentParser:
        return subparsers.add_parser("develop", help = "set up the workspace for development")


    def check_requirements(self, arguments: argparse.Namespace, **kwargs) -> None:
        pass


    def run(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        automation_configuration: AutomationConfiguration = kwargs["configuration"]

        venv_directory = automation_configuration.python_development_configuration.venv_directory
        python_system_executable = python_helpers.resolve_system_python_executable()
        python_environment = PythonEnvironment(python_system_executable, venv_directory)

        package_collection_for_pip: List[str] = []
        for package in automation_configuration.python_development_configuration.package_collection:
            package_collection_for_pip.append(package.path_to_sources + "[all,dev]")

        logger.info("Setting up python virtual environment (Path: %s)", venv_directory)
        python_environment.setup_virtual_environment(simulate = simulate)
        python_environment.install_python_packages_for_development(package_collection_for_pip, simulate = simulate)


    async def run_async(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        self.run(arguments, simulate = simulate, **kwargs)
