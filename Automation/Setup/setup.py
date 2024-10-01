# cspell:words pyvenv

import argparse
import logging
import os
import sys
from typing import Optional

import automation_helpers
import python_helpers


logger = logging.getLogger("Main")


venv_directory = ".venv-automation"


def main() -> None:
    with automation_helpers.execute_in_workspace(__file__):
        arguments = parse_arguments()
        automation_helpers.configure_logging(arguments.verbosity)
        project_configuration = automation_helpers.load_project_configuration(".")

        log_script_information(project_configuration, simulate = arguments.simulate)

        setup_workspace(verbosity = arguments.verbosity, simulate = arguments.simulate)


def parse_arguments() -> argparse.Namespace:
    all_log_levels = [ "debug", "info", "warning", "error", "critical" ]

    main_parser = argparse.ArgumentParser()
    main_parser.add_argument("--simulate", action = "store_true",
        help = "perform a test run, without writing changes")
    main_parser.add_argument("--verbosity", choices = all_log_levels, default = "info", type = str.lower,
        metavar = "<level>", help = "set the logging level (%s)" % ", ".join(all_log_levels))

    return main_parser.parse_args()


def log_script_information(configuration: dict, simulate: bool = False) -> None:
    if simulate:
        logger.info("(( The script is running as a simulation ))")
        logger.info("")

    logger.info("%s %s", configuration["ProjectDisplayName"], configuration["ProjectVersionFull"])
    logger.info("Script executing in '%s'", os.getcwd())
    logger.info("")


def setup_workspace(verbosity: Optional[str] = None, simulate: bool = False) -> None:
    if verbosity is None:
        verbosity = "info"

    python_system_executable = python_helpers.resolve_system_python_executable()
    venv_python_executable = python_helpers.get_venv_executable(venv_directory, "python")
    pip_configuration_file_path = "pip.conf"
    python_package_collection = [ os.path.join("Automation", "Scripts[dev]") ]

    logger.info("Setting up python virtual environment for automation (Path: %s)", venv_directory)
    python_helpers.setup_virtual_environment(python_system_executable, venv_directory, pip_configuration_file_path, simulate = simulate)
    python_helpers.install_python_packages_for_development(venv_python_executable, python_package_collection, simulate = simulate)


if __name__ == "__main__":
    try:
        main()
    except Exception: # pylint: disable = broad-except
        logger.error("Script failed", exc_info = True)
        sys.exit(1)
