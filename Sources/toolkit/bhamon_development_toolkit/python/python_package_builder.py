import logging
import os
import re
import shutil
import sys
from typing import Optional

from bhamon_development_toolkit.processes import process_helpers
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_output_collector import ProcessOutputCollector
from bhamon_development_toolkit.processes.process_output_logger import ProcessOutputLogger
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.python.python_package import PythonPackage
from bhamon_development_toolkit.python.python_package_metadata import PythonPackageMetadata


logger = logging.getLogger("Python")


class PythonPackageBuilder:


    def __init__(self, python_executable: str, process_runner: ProcessRunner) -> None:
        self._python_executable = python_executable
        self._process_runner = process_runner


    def generate_package_metadata(self,
            python_package: PythonPackage, python_package_metadata: PythonPackageMetadata, simulate: bool = False) -> None:

        metadata_file_path = os.path.join(python_package.path_to_sources, python_package.name_for_file_system, "__metadata__.py")

        metadata_content = ""
        metadata_content += "__product__ = %r\n" % python_package_metadata.product_identifier
        metadata_content += "__version__ = %r\n" % python_package_metadata.version_identifier
        metadata_content += "__date__ = %r\n" % python_package_metadata.revision_date_as_string
        metadata_content += "__copyright__ = %r\n" % python_package_metadata.copyright_text

        logger.debug("Writing '%s'", metadata_file_path)
        if not simulate:
            with open(metadata_file_path, mode = "w", encoding = "utf-8") as metadata_file:
                metadata_file.writelines(metadata_content)


    def get_distribution_package_file_name(self, python_package: PythonPackage, version: str) -> str:
        return "{name}-{version}-py3-none-any.whl".format(name = python_package.name_for_file_system, version = version)


    async def build_distribution_package(self,
            python_package: PythonPackage, output_directory: str, log_file_path: Optional[str] = None, simulate: bool = False) -> None:

        setup_command = ExecutableCommand(self._python_executable)
        setup_command.add_arguments([ "-m", "pip", "wheel", "--no-deps", "--wheel-dir", output_directory, python_package.path_to_sources ])

        process_options = ProcessOptions()
        raw_logger = process_helpers.create_raw_logger(stream = sys.stdout, log_file_path = log_file_path)
        process_output_logger = ProcessOutputLogger(raw_logger.get_actual_logger())
        process_output_collector = ProcessOutputCollector()

        logger.info("+ %s", process_helpers.format_executable_command(setup_command.get_command_for_logging()))

        try:
            if not simulate:
                os.makedirs(output_directory, exist_ok = True) # Pip creates the output directory but use lowercase for some reason
                await self._process_runner.run(setup_command, process_options, [ process_output_logger, process_output_collector ])
        finally:
            raw_logger.dispose()

        filename_regex = r" filename=(" + re.escape(python_package.name_for_file_system) + r"-[0-9a-zA-Z\.\-\+]+-py3-none-any.whl) "
        filename_match = re.search(filename_regex, process_output_collector.get_stdout())

        output_path = "__unknown__"
        if filename_match is not None:
            output_path = os.path.join(output_directory, filename_match.group(1))

        logger.debug("Distribution package path: '%s'", output_path)
        if log_file_path is not None:
            logger.debug("Process log file: '%s'", log_file_path)


    def copy_distribution_package_for_release(self, # pylint: disable = too-many-arguments
            python_package: PythonPackage, version: str, version_for_release: str, distribution_directory: str, simulate: bool = False) -> None:

        archive_name = python_package.name_for_file_system + "-" + version
        archive_name_for_release = python_package.name_for_file_system + "-" + version_for_release
        source_path = os.path.join(distribution_directory, archive_name + "-py3-none-any.whl")
        destination_path = os.path.join(distribution_directory, archive_name_for_release + "-py3-none-any.whl")

        if not simulate:
            archive_staging_directory = os.path.join(destination_path + ".staging")
            if os.path.exists(archive_staging_directory):
                shutil.rmtree(archive_staging_directory)

            shutil.unpack_archive(source_path, archive_staging_directory, "zip")
            os.rename(os.path.join(archive_staging_directory, archive_name + ".dist-info"),
                os.path.join(archive_staging_directory, archive_name_for_release + ".dist-info"))

            metadata_file_path = os.path.join(archive_staging_directory, archive_name_for_release + ".dist-info", "METADATA")
            self.update_metadata(metadata_file_path, "Version", version_for_release)

            if os.path.exists(destination_path):
                os.remove(destination_path)

            logger.debug("Writing '%s'", destination_path)
            shutil.make_archive(destination_path + ".tmp", "zip", archive_staging_directory)
            os.replace(destination_path + ".tmp.zip", destination_path)
            shutil.rmtree(archive_staging_directory)

        logger.debug("Distribution package path: '%s'", destination_path)


    def update_metadata(self, metadata_file_path: str, key: str, value: str) -> None:
        with open(metadata_file_path, mode = "r", encoding = "utf-8") as metadata_file:
            metadata = metadata_file.read()

        metadata = re.sub(r"^" + re.escape(key) + r": .*$", key + ": " + value, metadata, flags = re.MULTILINE)

        with open(metadata_file_path, mode = "w", encoding = "utf-8") as metadata_file:
            metadata_file.write(metadata)
