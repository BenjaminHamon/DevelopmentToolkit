import argparse
import logging
import os
import uuid
from typing import List, Optional

from bhamon_development_toolkit.automation.automation_command import AutomationCommand
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner
from bhamon_development_toolkit.python import python_helpers
from bhamon_development_toolkit.python.pylint_runner import PylintRunner
from bhamon_development_toolkit.python.pylint_scope import PylintScope
from bhamon_development_toolkit.python.python_environment import PythonEnvironment
from bhamon_development_toolkit.python.python_package import PythonPackage

from automation_scripts.configuration.automation_configuration import AutomationConfiguration


logger = logging.getLogger("Main")


class LintCommand(AutomationCommand):


    def configure_argument_parser(self, subparsers: argparse._SubParsersAction, **kwargs) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser = subparsers.add_parser("lint", help = "run pylint on the Python packages")
        parser.add_argument("--run-identifier", metavar = "<identifier>", help = "set the identifier for the run")
        return parser


    def check_requirements(self, arguments: argparse.Namespace, **kwargs) -> None:
        pass


    def run(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        raise NotImplementedError("Not supported")


    async def run_async(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        automation_configuration: AutomationConfiguration = kwargs["configuration"]
        run_identifier: Optional[str] = arguments.run_identifier

        if run_identifier is None:
            run_identifier = str(uuid.uuid4())

        venv_directory = automation_configuration.python_development_configuration.venv_directory
        python_system_executable = python_helpers.resolve_system_python_executable()
        python_environment = PythonEnvironment(python_system_executable, venv_directory)
        process_runner = ProcessRunner(ProcessSpawner(is_console = True))
        pylint_runner = PylintRunner(process_runner, python_environment.get_venv_python_executable())

        all_python_scopes: List[PylintScope] = []
        for python_package in automation_configuration.python_development_configuration.package_collection:
            all_python_scopes.extend(get_scopes(python_package))

        result_directory = os.path.join("Artifacts", "LintResults")

        await pylint_runner.run(all_python_scopes, run_identifier, result_directory, simulate = simulate)


def get_scopes(python_package: PythonPackage) -> List[PylintScope]:
    scopes_for_package: List[PylintScope] = []

    scopes_for_package.append(PylintScope(
        identifier = python_package.identifier,
        path_or_module = os.path.join(python_package.path_to_sources, python_package.name_for_file_system)))

    if python_package.path_to_tests is not None:
        scopes_for_package.append(PylintScope(
            identifier = python_package.identifier + "-tests",
            path_or_module = os.path.join(python_package.path_to_tests, python_package.name_for_file_system + "_tests" )))

    return scopes_for_package
