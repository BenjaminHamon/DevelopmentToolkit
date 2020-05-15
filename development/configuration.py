import datetime
import importlib
import subprocess
import sys


def load_configuration(environment):
	configuration = {
		"project_identifier": "bhamon-development-toolkit",
		"project_name": "Development Toolkit",
		"project_version": load_project_version(environment["git_executable"], "1.0"),
	}

	configuration["author"] = "Benjamin Hamon"
	configuration["author_email"] = "hamon.benjamin@gmail.com"
	configuration["project_url"] = "https://github.com/BenjaminHamon/DevelopmentToolkit"
	configuration["copyright"] = "Copyright (c) 2019 Benjamin Hamon"

	configuration["development_dependencies"] = [ "pylint", "wheel" ]

	configuration["components"] = [
		{ "name": "bhamon-development-toolkit", "path": "toolkit" },
	]

	configuration["artifact_directory"] = "artifacts"

	return configuration


def load_project_version(git_executable, identifier):
	branch = subprocess.check_output([ git_executable, "rev-parse", "--abbrev-ref", "HEAD" ], universal_newlines = True).strip()
	revision = subprocess.check_output([ git_executable, "rev-parse", "--short=10", "HEAD" ], universal_newlines = True).strip()
	revision_date = int(subprocess.check_output([ git_executable, "show", "--no-patch", "--format=%ct", revision ], universal_newlines = True).strip())
	revision_date = datetime.datetime.utcfromtimestamp(revision_date).replace(microsecond = 0).isoformat() + "Z"

	return {
		"identifier": identifier,
		"numeric": identifier,
		"full": identifier + "+" + revision,
		"branch": branch,
		"revision": revision,
		"date": revision_date,
	}


def get_setuptools_parameters(configuration):
	return {
		"version": configuration["project_version"]["full"],
		"author": configuration["author"],
		"author_email": configuration["author_email"],
		"url": configuration["project_url"],
	}


def load_commands():
	all_modules = [
		"development.commands.clean",
		"development.commands.develop",
		"development.commands.distribute",
		"development.commands.info",
		"development.commands.lint",
	]

	return [ import_command(module) for module in all_modules ]


def import_command(module_name):
	try:
		return {
			"module_name": module_name,
			"module": importlib.import_module(module_name),
		}

	except ImportError:
		return {
			"module_name": module_name,
			"exception": sys.exc_info(),
		}
