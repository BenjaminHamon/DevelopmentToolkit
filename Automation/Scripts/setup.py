import os
import sys

import setuptools

workspace_directory = os.path.abspath(os.path.join("..", ".."))
automation_setup_directory = os.path.join(workspace_directory, "Automation", "Setup")

sys.path.insert(0, automation_setup_directory)

import automation_helpers # pylint: disable = import-error, wrong-import-position


def run_setup() -> None:
    project_configuration = automation_helpers.load_project_configuration(workspace_directory)

    setuptools.setup(
		name = "automation-scripts",
		description = "Automation scripts for %s" % project_configuration["ProjectDisplayName"],
        version = project_configuration["ProjectVersionFull"],
        author = project_configuration["Author"],
        author_email = project_configuration["AuthorEmail"],
        url = project_configuration["ProjectUrl"],
        packages = setuptools.find_packages(include = [ "automation_scripts", "automation_scripts.*" ]),

        python_requires = "~= 3.9",

        extras_require = {
            "dev": [
                "mockito ~= 1.4.0",
                "pylint ~= 2.17.5",
                "pytest ~= 7.4.0",
                "pytest-asyncio ~= 0.21.1",
                "pytest-json ~= 0.4.0",
                "twine ~= 4.0.2",
            ],
        },
    )


run_setup()
