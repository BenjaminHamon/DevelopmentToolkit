import argparse
import glob
import logging
import os
import shutil
from typing import List

from bhamon_development_toolkit.automation.automation_command import AutomationCommand
from bhamon_development_toolkit.python.python_package import PythonPackage

from automation_scripts.configuration.project_configuration import ProjectConfiguration


logger = logging.getLogger("Main")


class CleanCommand(AutomationCommand):


    def configure_argument_parser(self, subparsers: argparse._SubParsersAction, **kwargs) -> argparse.ArgumentParser:
        return subparsers.add_parser("clean", help = "clean the workspace")


    def check_requirements(self, arguments: argparse.Namespace, **kwargs) -> None:
        pass


    def run(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        project_configuration: ProjectConfiguration = kwargs["configuration"]

        logger.info("Cleaning the workspace")
        logger.info("")

        logger.info("Cleaning artifacts")
        self.clean_artifacts("Artifacts", simulate = simulate)
        logger.debug("")

        logger.info("Cleaning python sources")
        self.clean_python_sources(project_configuration.list_python_packages(), simulate = simulate)
        logger.debug("")

        logger.info("Cleaning python tests")
        self.clean_python_tests(simulate = simulate)
        logger.debug("")

        logger.info("Cleaning automation")
        self.clean_automation(project_configuration.list_automation_packages(), simulate = simulate)
        logger.debug("")


    async def run_async(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        self.run(arguments, simulate = simulate, **kwargs)


    def clean_artifacts(self, artifact_directory: str, simulate: bool = False) -> None:
        self._remove_directory(artifact_directory, simulate = simulate)


    def clean_python_sources(self, python_package_collection: List[PythonPackage], simulate: bool = False) -> None:
        for python_package in python_package_collection:
            self._clean_python_package(python_package, simulate = simulate)


    def clean_python_tests(self, simulate: bool = False) -> None:
        self._clean_pytest_cache(simulate = simulate)


    def clean_automation(self, python_package_collection: List[PythonPackage], simulate: bool = False) -> None:
        for python_package in python_package_collection:
            self._clean_python_package(python_package, simulate = simulate)
        self._clean_python_cache(os.path.join("Automation", "Setup"), simulate = simulate)


    def _clean_python_package(self, python_package: PythonPackage, simulate: bool = False) -> None:
        directories_to_remove = [
            os.path.join(python_package.path_to_sources, "build"),
            os.path.join(python_package.path_to_sources, "dist"),
            os.path.join(python_package.path_to_sources, python_package.name_for_file_system + ".egg-info"),
        ]

        for directory in directories_to_remove:
            self._remove_directory(directory, simulate = simulate)

        metadata_file_path = os.path.join(python_package.path_to_sources, python_package.name_for_file_system, "__metadata__.py")
        self._remove_file(metadata_file_path, simulate = simulate)

        self._clean_python_cache(python_package.path_to_sources, simulate = simulate)
        if python_package.path_to_tests is not None:
            self._clean_python_cache(python_package.path_to_tests, simulate = simulate)


    def _clean_python_cache(self, source_directory: str, simulate: bool = False) -> None:
        if not os.path.exists(source_directory):
            return

        directories_to_remove = glob.glob(os.path.join(source_directory, "**", "__pycache__"), recursive = True)

        for directory in directories_to_remove:
            self._remove_directory(directory, simulate = simulate)


    def _clean_pytest_cache(self, simulate: bool = False) -> None:
        directories_to_remove = [ ".pytest_cache" ]

        for directory in directories_to_remove:
            self._remove_directory(directory, simulate = simulate)


    def _remove_directory(self, directory_to_remove: str, simulate: bool = False) -> None:
        if os.path.exists(directory_to_remove):
            logger.debug("Removing '%s'", directory_to_remove)
            if not simulate:
                shutil.rmtree(directory_to_remove)


    def _remove_file(self, file_to_remove: str, simulate: bool = False) -> None:
        if os.path.exists(file_to_remove):
            logger.debug("Removing '%s'", file_to_remove)
            if not simulate:
                os.remove(file_to_remove)
