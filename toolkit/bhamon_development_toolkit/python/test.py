import datetime
import json
import logging
import os
import shutil
import subprocess


logger = logging.getLogger("Test")

pytest_status_collection = [ "error", "failed", "passed", "skipped", "xfailed", "xpassed" ]


def run_pytest(python_executable, result_directory, run_identifier, target, filter_expression, simulate): # pylint: disable = too-many-arguments, too-many-locals
	logger.info("Running test session (RunIdentifier: '%s', Target: '%s', Filter: '%s')", run_identifier, target, filter_expression)

	result_directory = os.path.join(result_directory, str(run_identifier))
	intermediate_report_file_path = os.path.join(result_directory, "test_report_intermediate.json")
	report_file_path = os.path.join(result_directory, "test_report.json")

	if not simulate:
		if os.path.exists(result_directory):
			shutil.rmtree(result_directory)
		os.makedirs(result_directory)

	pytest_command = [ python_executable, "-m", "pytest", target, "--verbose" ]
	pytest_command += [ "--collect-only" ] if simulate else []
	pytest_command += [ "--basetemp", result_directory ]
	pytest_command += [ "-k", filter_expression ] if filter_expression else []
	output_options = [ "--json", intermediate_report_file_path ] if not simulate else []

	start_date = datetime.datetime.utcnow().replace(microsecond = 0).isoformat() + "Z"

	logger.info("+ %s", " ".join(pytest_command))
	result_code = subprocess.call(pytest_command + output_options)

	success = result_code == 0
	completion_date = datetime.datetime.utcnow().replace(microsecond = 0).isoformat() + "Z"

	if simulate:
		intermediate_report = _simulate_intermediate_report()
	else:
		with open(intermediate_report_file_path, mode = "r") as intermediate_report_file:
			intermediate_report = json.load(intermediate_report_file)["report"]

	job_parameters = { "target": target, "filter_expression": filter_expression }
	report = _generate_report(run_identifier, job_parameters, intermediate_report, success, start_date, completion_date)

	if not simulate:
		with open(report_file_path, mode = "w") as report_file:
			json.dump(report, report_file, indent = 4)

	return report


def get_aggregated_results(all_report_file_paths):
	all_reports = []

	for report_file_path in all_report_file_paths:
		with open(report_file_path, mode = "r") as report_file:
			all_reports.append(json.load(report_file))

	success = True
	summary = { "total": 0 }
	summary.update({ status: 0 for status in pytest_status_collection })

	for report in all_reports:
		if report["job"] == "pytest":
			success = success and report["success"]
			summary["total"] += report["summary"]["total"]
			for status in pytest_status_collection:
				summary[status] += report["summary"][status]

	return {
		"run_type": "pytest",
		"success": success,
		"summary": summary,
	}


def _simulate_intermediate_report():
	return {
		"tests": [],
		"summary": {
			"num_tests": 0,
		},
	}


def _generate_report(run_identifier, job_parameters, intermediate_report, success, start_date, completion_date): # pylint: disable = too-many-arguments
	summary = { "total": intermediate_report["summary"]["num_tests"] }
	for status in pytest_status_collection:
		summary[status] = intermediate_report["summary"].get(status, 0)

	all_tests = []
	for test in intermediate_report["tests"]:
		all_tests.append({
			"name": test["name"],
			"status": test["outcome"],
			"duration": test["duration"],
		})

	return {
		"run_identifier": str(run_identifier),
		"job": "pytest",
		"job_parameters": job_parameters,
		"success": success,
		"summary": summary,
		"results": all_tests,
		"start_date": start_date,
		"completion_date": completion_date,
	}
