import abc
import logging
import os
import shutil
from typing import List, Optional, Tuple

from bhamon_development_toolkit.archives.archive_operations import ArchiveOperations


logger = logging.getLogger("ArchiveOperations")


class ArchiveOperationsBase(ArchiveOperations):


    def create(self, archive_path: str, mapping_collection: List[Tuple[str,str]], *, simulate: bool = False) -> None:
        """ Create an archive with mappings of path sources and destinations """

        logger.info("Writing archive '%s'", archive_path)

        if not simulate:
            if os.path.dirname(archive_path):
                os.makedirs(os.path.dirname(archive_path), exist_ok = True)

        if simulate:
            for source, destination in mapping_collection:
                logger.debug("+ '%s' => '%s'", source, destination)

        else:
            self._create_implementation(archive_path, mapping_collection)


    @abc.abstractmethod
    def _create_implementation(self, archive_path: str, mapping_collection: List[Tuple[str,str]]) -> None:
        pass


    def extract(self, # pylint: disable = too-many-arguments
            archive_path: str, output_directory: str, *,
            extraction_directory: Optional[str] = None,
            file_collection: Optional[List[str]] = None,
            replace: bool = False, simulate: bool = False) -> None:
        """ Extract an archive to the provided output directory """

        logger.info("Extracting archive '%s'", archive_path)

        if extraction_directory is None:
            extraction_directory = archive_path + ".extracting"

        if file_collection is None:
            file_collection = self.list_files(archive_path)

        self._extract_implementation(archive_path, extraction_directory, file_collection, simulate = simulate)
        self._apply_extraction_changes(output_directory, extraction_directory, file_collection, replace = replace, simulate = simulate)


    def _apply_extraction_changes(self, # pylint: disable = too-many-arguments
            output_directory: str, extraction_directory: str, file_collection: List[str], *, replace: bool = False, simulate: bool = False) -> None:

        if replace and os.path.isdir(output_directory):
            logger.debug("Removing existing files from '%s'", output_directory)
            if not simulate:
                shutil.rmtree(output_directory)

        logger.debug("Moving files to '%s'", output_directory)
        move_whole_directory = not os.path.isdir(output_directory)

        for file_path in file_collection:
            source = os.path.normpath(os.path.join(extraction_directory, file_path))
            destination = os.path.normpath(os.path.join(output_directory, file_path))
            logger.debug("+ '%s' => '%s'", source, destination)

            if not simulate and not move_whole_directory:
                if os.path.dirname(destination):
                    os.makedirs(os.path.dirname(destination), exist_ok = True)
                if os.path.exists(destination):
                    os.remove(destination)
                shutil.move(source, destination)

        if not simulate and move_whole_directory:
            if os.path.dirname(output_directory):
                os.makedirs(os.path.dirname(output_directory), exist_ok = True)
            shutil.move(extraction_directory, output_directory)

        if not simulate and not move_whole_directory:
            shutil.rmtree(extraction_directory)


    @abc.abstractmethod
    def _extract_implementation(self, archive_path: str, extraction_directory: str, file_collection: List[str], *, simulate: bool = False) -> None:
        pass
