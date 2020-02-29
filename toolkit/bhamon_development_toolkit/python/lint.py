import datetime
import json
import logging
import os
import subprocess


logger = logging.getLogger("Lint")


pylint_categories = [ "fatal", "error", "warning", "convention", "refactor" ]
pylint_message_separator = "|"
pylint_message_elements = [
	{ "key": "file_path", "pylint_field": "path" },
	{ "key": "line_in_file", "pylint_field": "line"},
	{ "key": "object", "pylint_field": "obj" },
	{ "key": "category", "pylint_field": "category" },
	{ "key": "identifier", "pylint_field": "symbol" },
	{ "key": "code", "pylint_field": "msg_id" },
	{ "key": "message", "pylint_field": "msg" },
]


def run_pylint(python_executable, result_directory, run_identifier, target, simulate): # pylint: disable = too-many-locals
	logger.info("Running linter (RunIdentifier: '%s', Target: '%s')", run_identifier, target)

	result_directory = os.path.join(result_directory, str(run_identifier))
	report_file_path = os.path.join(result_directory, os.path.normpath(target).replace(os.sep, "_") + ".json")

	if not simulate:
		os.makedirs(result_directory, exist_ok = True)

	pylint_command = [ python_executable, "-u", "-m", "pylint", target ]
	format_options = [ "--msg-template", pylint_message_separator.join([ "{" + element["pylint_field"] + "}" for element in pylint_message_elements ]) ]
	start_date = datetime.datetime.utcnow().replace(microsecond = 0).isoformat() + "Z"

	logger.info("+ %s", " ".join(pylint_command))

	if simulate:
		all_issues = []
		result_code = 0

	else:
		process = subprocess.Popen(pylint_command + format_options, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines = True)
		all_issues = _process_pylint_output(process.stdout)
		result_code = process.wait()

	success = result_code == 0
	completion_date = datetime.datetime.utcnow().replace(microsecond = 0).isoformat() + "Z"

	summary = {}
	for category in pylint_categories:
		summary[category] = len([ issue for issue in all_issues if issue["category"] == category ])

	if success:
		logger.info("Linting succeeded for '%s'", target)
	else:
		logger.error("Linting failed for '%s' (%s)", target, ", ".join("%s: %s" % (key, value) for key, value in summary.items() if value > 0))

	report = {
		"run_identifier": str(run_identifier),
		"job": "pylint",
		"job_parameters": { "target": target },
		"success": success,
		"summary": summary,
		"results": all_issues,
		"start_date": start_date,
		"completion_date": completion_date,
	}

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
	summary = { category: 0 for category in pylint_categories }

	for report in all_reports:
		if report["job"] == "pylint":
			success = success and report["success"]
			for category in pylint_categories:
				summary[category] += report["summary"][category]

	return {
		"run_type": "pylint",
		"success": success,
		"summary": summary,
	}


def _process_pylint_output(output):
	all_issues = []

	for line in output:
		line = line.rstrip()

		if pylint_message_separator in line:
			issue = _parse_pylint_issue(line)
			all_issues.append(issue)

			log_format = "(%s:%s) %s (%s, %s)"
			log_arguments = [ issue["file_path"], issue["line_in_file"], issue["message"],  issue["identifier"], issue["code"] ]

			if issue["category"] in [ "error", "fatal" ]:
				logger.error(log_format, *log_arguments)
			elif issue["category"] in [ "convention", "refactor", "warning" ]:
				logger.warning(log_format, *log_arguments)
			else:
				raise ValueError("Unhandled issue category '%s'" % issue["category"])

	return all_issues


def _parse_pylint_issue(line):
	result = {}

	message_elements = line.split(pylint_message_separator)
	for index, element in enumerate(pylint_message_elements):
		result[element["key"]] = message_elements[index]

	result["file_path"] = os.path.relpath(result["file_path"])

	return result
