import glob
import logging
import os
import shutil
import uuid

import bhamon_development_toolkit.python.lint as python_lint
import bhamon_development_toolkit.workspace as workspace


logger = logging.getLogger("Main")


def configure_argument_parser(environment, configuration, subparsers): # pylint: disable = unused-argument
	return subparsers.add_parser("lint", help = "run linter")


def run(environment, configuration, arguments): # pylint: disable = unused-argument
	run_identifier = str(uuid.uuid4())
	session_success = True

	if not arguments.simulate:
		if os.path.exists(os.path.join("test_results", run_identifier)):
			shutil.rmtree(os.path.join("test_results", run_identifier))
		os.makedirs(os.path.join("test_results", run_identifier))

	for component in configuration["components"]:
		pylint_results = python_lint.run_pylint(environment["python3_executable"], "test_results", run_identifier, component["name"].replace("-", "_"), simulate = arguments.simulate)
		if not pylint_results["success"]:
			session_success = False

		print("")

	if arguments.results:
		save_results(arguments.results, "test_results", run_identifier, simulate = arguments.simulate)

	if not session_success:
		raise RuntimeError("Linting failed")


def save_results(result_file_path, result_directory, run_identifier, simulate):
	all_report_file_paths = glob.glob(os.path.join(result_directory, run_identifier, "*.json"))
	reports_as_results = python_lint.get_aggregated_results(all_report_file_paths)

	results = workspace.load_results(result_file_path)
	results["tests"] = results.get("tests", [])
	results["tests"].append(reports_as_results)

	if not simulate:
		workspace.save_results(result_file_path, results)
