import setuptools

import environment
import configuration


environment_instance = environment.load_environment()
configuration_instance = configuration.load_configuration(environment_instance)
parameters = configuration.get_setuptools_parameters(configuration_instance)


parameters.update({
	"name": "bhamon-dev-scripts",
	"description": "Toolkit for software development scripts",
	"packages": [ "bhamon_dev_scripts" ],
	"python_requires": "~= 3.5",
})

setuptools.setup(**parameters)
