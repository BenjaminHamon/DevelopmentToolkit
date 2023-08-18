import argparse
import logging
import os
import sys
from typing import List, Optional
import uuid

from bhamon_development_toolkit.automation.automation_command import AutomationCommand
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner
from bhamon_development_toolkit.python.pytest_runner import PytestRunner
from bhamon_development_toolkit.python.pytest_scope import PytestScope

from automation_scripts.configuration.project_configuration import ProjectConfiguration


logger = logging.getLogger("Main")


class TestCommand(AutomationCommand):


    def configure_argument_parser(self, subparsers: argparse._SubParsersAction, **kwargs) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser = subparsers.add_parser("test", help = "run tests from the Python packages")
        parser.add_argument("--run-identifier", metavar = "<identifier>", help = "set the identifier for the run")
        return parser


    def check_requirements(self, arguments: argparse.Namespace, **kwargs) -> None:
        pass


    def run(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        raise NotImplementedError("Not supported")


    async def run_async(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        project_configuration: ProjectConfiguration = kwargs["configuration"]

        process_runner = ProcessRunner(ProcessSpawner(is_console = True))
        pytest_runner = PytestRunner(process_runner, sys.executable)

        all_python_scopes: List[PytestScope] = []
        for python_package in project_configuration.list_python_packages():
            if python_package.path_to_tests is None:
                raise ValueError("Python package '%s' has no tests" % python_package.identifier)
            all_python_scopes.append(PytestScope(identifier = python_package.identifier, path = python_package.path_to_tests, filter_expression = None))

        run_identifier: Optional[str] = arguments.run_identifier
        if run_identifier is None:
            run_identifier = str(uuid.uuid4())

        result_directory = os.path.join("Artifacts", "TestResults")

        await pytest_runner.run(all_python_scopes, run_identifier, result_directory, simulate = simulate)
