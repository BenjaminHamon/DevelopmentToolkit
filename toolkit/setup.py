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
		"packages": [ "bhamon_dev_scripts" ],
		"python_requires": "~= 3.5",
	})

	generate_metadata(configuration_instance, parameters["packages"][0], False)
	setuptools.setup(**parameters)


def generate_metadata(configuration_instance, package_name, simulate):
	metadata_file_path = os.path.join(package_name, "__metadata__.py")
	metadata_content = ""
	metadata_content += "__copyright__ = \"%s\"\n" % configuration_instance["copyright"]
	metadata_content += "__version__ = \"%s\"\n" % configuration_instance["project_version"]["full"]
	metadata_content += "__date__ = \"%s\"\n" % configuration_instance["project_version"]["date"]

	if not simulate:
		with open(metadata_file_path, "w", encoding = "utf-8") as metadata_file:
			metadata_file.writelines(metadata_content)


run_setup()
