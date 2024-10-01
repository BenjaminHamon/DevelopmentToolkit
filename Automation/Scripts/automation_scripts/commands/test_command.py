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

from automation_scripts.configuration.automation_configuration import AutomationConfiguration


logger = logging.getLogger("Main")


class TestCommand(AutomationCommand):


    def configure_argument_parser(self, subparsers: argparse._SubParsersAction, **kwargs) -> argparse.ArgumentParser:
        parser: argparse.ArgumentParser = subparsers.add_parser("test", help = "run tests from the Python packages")
        parser.add_argument("--run-identifier", metavar = "<identifier>", help = "set the identifier for the run")
        parser.add_argument("--filters", nargs = "*", metavar = "<expression>", help = "set filter expressions for selecting tests")
        return parser


    def check_requirements(self, arguments: argparse.Namespace, **kwargs) -> None:
        pass


    def run(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        raise NotImplementedError("Not supported")


    async def run_async(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        automation_configuration: AutomationConfiguration = kwargs["configuration"]
        run_identifier: Optional[str] = arguments.run_identifier
        all_filter_expressions: Optional[List[str]] = arguments.filters

        if run_identifier is None:
            run_identifier = str(uuid.uuid4())

        process_runner = ProcessRunner(ProcessSpawner(is_console = True))
        pytest_runner = PytestRunner(process_runner, sys.executable)

        all_python_scopes: List[PytestScope] = []
        for python_package in automation_configuration.project_python_elements.package_collection:
            if python_package.path_to_tests is None:
                raise ValueError("Python package '%s' has no tests" % python_package.identifier)
            for filter_expression in (all_filter_expressions if all_filter_expressions is not None else [ None ]):
                all_python_scopes.append(PytestScope(python_package.identifier, python_package.path_to_tests, filter_expression))

        result_directory = os.path.join("Artifacts", "TestResults")

        await pytest_runner.run(all_python_scopes, run_identifier, result_directory, simulate = simulate)
