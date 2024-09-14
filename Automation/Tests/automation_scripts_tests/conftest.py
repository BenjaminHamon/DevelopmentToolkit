import datetime
import os

import mockito
import pytest

from bhamon_development_toolkit.automation.project_version import ProjectVersion
from bhamon_development_toolkit.python.python_package import PythonPackage

from automation_scripts.configuration.automation_configuration import AutomationConfiguration
from automation_scripts.configuration.project_metadata import ProjectMetadata
from automation_scripts.configuration.project_python_elements import ProjectPythonElements
from automation_scripts.configuration.workspace_environment import WorkspaceEnvironment


@pytest.fixture
def automation_configuration() -> AutomationConfiguration:
    project_metadata = ProjectMetadata(
        identifier = "MyProjectIdentifier",
        display_name = "My Project Display Name",
        version = ProjectVersion(
            identifier = "1.0",
            revision = "abcde",
            revision_date = datetime.datetime(2020, 1, 1),
            branch = "active-branch"),
        copyright_text = "Copyright (c) 2020 The Project Author",
        author = "The Project Author",
        author_email = "the-project-author@example.com",
        project_url = "www.example.com")

    python_project_elements = ProjectPythonElements(
        package_collection = [
            PythonPackage(
                identifier = "the-fake-project",
                path_to_sources = "Sources",
                path_to_tests = "Tests"),
        ]
    )

    workspace_environment = mockito.mock(spec = WorkspaceEnvironment)

    automation_python_package = PythonPackage(
        identifier = "automation-scripts-fake",
        path_to_sources = os.path.join("Automation", "Scripts"),
        path_to_tests = os.path.join("Automation", "Tests"))

    return AutomationConfiguration(
        project_metadata = project_metadata,
        project_python_elements = python_project_elements,
        workspace_environment = workspace_environment, # type: ignore
        automation_python_package = automation_python_package,
    )


@pytest.fixture
def workspace(tmpdir, automation_configuration) -> str: # pylint: disable = redefined-outer-name
    workspace_directory = str(tmpdir)

    for python_package in automation_configuration.project_python_elements.package_collection:
        os.makedirs(os.path.join(tmpdir, python_package.path_to_sources, python_package.name_for_file_system))
        if python_package.path_to_tests is not None:
            os.makedirs(os.path.join(tmpdir, python_package.path_to_tests, python_package.name_for_file_system + "_tests"))

    return workspace_directory
