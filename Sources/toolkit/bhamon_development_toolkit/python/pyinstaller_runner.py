# cspell:words distpath filevers noconfirm onefile prodvers pyinstaller specpath workpath

import logging
import os
import platform
import sys
from typing import List, Optional

from bhamon_development_toolkit.applications import application_version_helpers
from bhamon_development_toolkit.applications.application_metadata import ApplicationMetadata
from bhamon_development_toolkit.processes import process_helpers
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_logger import ProcessOutputLogger
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.python.pyinstaller_configuration import PyInstallerConfiguration


logger = logging.getLogger("PyInstaller")


class PyInstallerRunner:


    def __init__(self, process_runner: ProcessRunner, pyinstaller_executable: str) -> None:
        self._process_runner = process_runner
        self._pyinstaller_executable = pyinstaller_executable


    async def run(self, # pylint: disable = too-many-arguments
            configuration: PyInstallerConfiguration, output_directory: str, intermediate_directory: str,
            clean: bool = False, log_level: Optional[str] = None, log_file_path: Optional[str] = None, simulate: bool = False) -> None:

        executable_path = os.path.join(output_directory, configuration.executable_name)
        if platform.system() == "Windows":
            executable_path += ".exe"

        command = ExecutableCommand(self._pyinstaller_executable)
        command.add_arguments([ "--distpath", output_directory ])
        command.add_arguments([ "--name", configuration.executable_name ])
        command.add_arguments([ "--specpath", intermediate_directory ])
        command.add_arguments([ "--workpath", intermediate_directory ])

        if configuration.single_file:
            command.add_arguments([ "--onefile" ])

        if platform.system() == "Windows" and configuration.windows_version_info_file_path is not None:
            command.add_arguments([ "--version-file", os.path.abspath(configuration.windows_version_info_file_path) ])

        command.add_internal_arguments([ "--noconfirm" ], [])

        if clean:
            command.add_arguments([ "--clean" ])
        if log_level is not None:
            command.add_internal_arguments([ "--log-level", log_level.upper() ], [])

        command.add_arguments([ configuration.application_source_file_path ])

        process_options = ProcessOptions()
        raw_logger = process_helpers.create_raw_logger(stream = sys.stdout, log_file_path = log_file_path)
        process_output_logger = ProcessOutputLogger(raw_logger.get_actual_logger())

        logger.debug("+ %s", process_helpers.format_executable_command(command.get_command_for_logging()))

        try:
            if not simulate:
                await self._process_runner.run(command, process_options, [ process_output_logger ], check_exit_code = True)
        finally:
            if log_file_path is not None:
                logger.debug("Process log file: '%s'", log_file_path)
            raw_logger.dispose()

        logger.debug("Application executable path: '%s'", executable_path)


    def generate_windows_version_info(self, application_metadata: ApplicationMetadata) -> str:
        version_as_numeric_tuple = \
            application_version_helpers.convert_version_to_numeric_tuple(application_metadata.version_identifier, expected_size = 4)

        rc_as_text = """
VSVersionInfo(
    ffi = FixedFileInfo(
        filevers = {version_as_numeric_tuple},
        prodvers = {version_as_numeric_tuple},
    ),
    kids = [
        StringFileInfo([
            StringTable(
                "040904B0",
                [
{fields}
                ])
        ]),
		VarFileInfo([VarStruct("Translation", [1033, 1200])])
    ]
)
"""

        field_line_template = """                    StringStruct("{key}", "{value}"),"""

        fields_as_text_lines: List[str] = []
        fields_as_text_lines.append(field_line_template.format(key = "ProductName", value = application_metadata.product_identifier))
        fields_as_text_lines.append(field_line_template.format(key = "ProductVersion", value = application_metadata.version_identifier_full))
        fields_as_text_lines.append(field_line_template.format(key = "FileVersion", value = application_metadata.version_identifier))

        if application_metadata.product_copyright is not None:
            fields_as_text_lines.append(field_line_template.format(key = "LegalCopyright", value = application_metadata.product_copyright))

        rc_as_text = rc_as_text.lstrip()

        rc_as_text = rc_as_text.format(
            version_as_numeric_tuple = "(%s)" % ", ".join(str(x) for x in version_as_numeric_tuple),
            fields = "\n".join(fields_as_text_lines),
        )

        return rc_as_text
