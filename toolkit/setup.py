import os
import sys

import setuptools

sys.path.insert(0, os.path.join(sys.path[0], ".."))

import development.configuration # pylint: disable = wrong-import-position
import development.environment # pylint: disable = wrong-import-position


def run_setup():
	environment_instance = development.environment.load_environment()
	configuration_instance = development.configuration.load_configuration(environment_instance)
	parameters = development.configuration.get_setuptools_parameters(configuration_instance)

	parameters.update({
		"name": "bhamon-development-toolkit",
		"description": "Toolkit for software development scripts",

		"packages": [
			"bhamon_development_toolkit",
			"bhamon_development_toolkit/artifacts",
			"bhamon_development_toolkit/python",
		],

		"python_requires": "~= 3.5",
	})

	setuptools.setup(**parameters)


run_setup()
