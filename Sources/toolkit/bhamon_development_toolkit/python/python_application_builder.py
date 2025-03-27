# cspell:words pyinstaller

import logging
import os
import platform
from typing import Optional

from bhamon_development_toolkit.applications.application_metadata import ApplicationMetadata
from bhamon_development_toolkit.python.pyinstaller_configuration import PyInstallerConfiguration
from bhamon_development_toolkit.python.pyinstaller_runner import PyInstallerRunner


logger = logging.getLogger("PythonApplicationBuilder")


class PythonApplicationBuilder:


    def __init__(self, pyinstaller_runner: PyInstallerRunner) -> None:
        self._pyinstaller_runner = pyinstaller_runner


    async def build_application(self, # pylint: disable = too-many-arguments
            application_source_file_path: str, executable_name: str, output_directory: str, intermediate_directory: str, *,
            application_metadata: Optional[ApplicationMetadata] = None, log_file_path: Optional[str] = None, simulate: bool = False) -> None:

        pyinstaller_configuration = PyInstallerConfiguration(
            application_source_file_path = application_source_file_path,
            executable_name = executable_name,
            single_file = True,
            windows_version_info_file_path = os.path.join(intermediate_directory, "Application.rc") if platform.system() == "Windows" else None,
        )

        if platform.system() == "Windows" and application_metadata is not None:
            if pyinstaller_configuration.windows_version_info_file_path is None:
                raise ValueError("Version info file path must be set")

            windows_version_info = self._pyinstaller_runner.generate_windows_version_info(application_metadata)
            with open(pyinstaller_configuration.windows_version_info_file_path, mode = "w", encoding = "utf-8") as windows_version_info_file:
                windows_version_info_file.write(windows_version_info)

        await self._pyinstaller_runner.run(
            configuration = pyinstaller_configuration,
            output_directory = output_directory,
            intermediate_directory = intermediate_directory,
            clean = True,
            log_level = "debug",
            log_file_path = log_file_path,
            simulate = simulate)
