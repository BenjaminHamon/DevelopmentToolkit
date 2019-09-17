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
		"name": "bhamon-dev-scripts",
		"description": "Toolkit for software development scripts",

		"packages": [
			"bhamon_dev_scripts",
			"bhamon_dev_scripts/python",
		],

		"python_requires": "~= 3.5",
	})

	setuptools.setup(**parameters)


run_setup()
