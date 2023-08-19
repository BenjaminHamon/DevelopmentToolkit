import argparse
import logging
import os
import sys
from typing import List, Optional
import uuid

from bhamon_development_toolkit.automation.automation_command import AutomationCommand
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner
from bhamon_development_toolkit.python.pylint_runner import PylintRunner
from bhamon_development_toolkit.python.pylint_scope import PylintScope

from automation_scripts.configuration.project_configuration import ProjectConfiguration


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
        project_configuration: ProjectConfiguration = kwargs["configuration"]

        process_runner = ProcessRunner(ProcessSpawner(is_console = True))
        pylint_runner = PylintRunner(process_runner, sys.executable)

        all_python_scopes: List[PylintScope] = []
        for python_package in project_configuration.list_python_packages():
            all_python_scopes.append(PylintScope(identifier = python_package.identifier, path_or_module = python_package.name_for_module_import))

        run_identifier: Optional[str] = arguments.run_identifier
        if run_identifier is None:
            run_identifier = str(uuid.uuid4())

        result_directory = os.path.join("Artifacts", "LintResults")

        await pylint_runner.run(all_python_scopes, run_identifier, result_directory, simulate = simulate)
