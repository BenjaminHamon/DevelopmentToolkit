from bhamon_development_toolkit.python.python_package import PythonPackage

from automation_scripts.configuration.project_metadata import ProjectMetadata
from automation_scripts.configuration.project_python_elements import ProjectPythonElements
from automation_scripts.configuration.workspace_environment import WorkspaceEnvironment


class AutomationConfiguration:


    def __init__(self,
            project_metadata: ProjectMetadata,
            project_python_elements: ProjectPythonElements,
            workspace_environment: WorkspaceEnvironment,
            automation_python_package: PythonPackage) -> None:

        self.project_metadata = project_metadata
        self.project_python_elements = project_python_elements
        self.workspace_environment = workspace_environment
        self.automation_python_package = automation_python_package
