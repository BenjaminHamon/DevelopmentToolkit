class WorkspaceEnvironment:


    def get_python_package_repository_url(self, target_environment: str) -> str:
        if target_environment == "Development":
            return "https://nexus.benjaminhamon.com/repository/python-packages-development"
        if target_environment == "Production":
            return "https://nexus.benjaminhamon.com/repository/python-packages"

        raise ValueError("Unknown environment: '%s'" % target_environment)
