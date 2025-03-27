import logging
import os
import tarfile
from typing import List, Optional, Tuple

from bhamon_development_toolkit.archives.archive_operations_base import ArchiveOperationsBase


logger = logging.getLogger("ArchiveOperations")


class TarArchiveOperations(ArchiveOperationsBase):


    def __init__(self, compression: Optional[str] = None) -> None:
        self._compression = compression


    def get_file_extension(self) -> str:
        if self._compression is None:
            return ".tar"
        if self._compression == "bz2":
            return ".tar.bz2"
        if self._compression == "gz":
            return ".tar.gz"

        raise ValueError("Unsupported compression: %s" % self._compression)


    def _create_implementation(self, archive_path: str, mapping_collection: List[Tuple[str, str]]) -> None:
        mode = "w" if self._compression is None else "w:" + self._compression

        # VSCode shows reportCallIssue here, apparently because it doesn't detects all allowed values for mode
        with tarfile.open(archive_path, mode = mode, format = tarfile.GNU_FORMAT) as archive_file: # type: ignore
            for source, destination in mapping_collection:
                destination = os.path.normpath(destination).replace("\\", "/")
                logger.debug("+ '%s' => '%s'", source, destination)
                archive_file.add(source, destination)


    def list_files(self, archive_path: str)-> List[str]:
        with tarfile.open(archive_path, mode = "r") as archive_file:
            return [ x.path for x in archive_file.getmembers() ]


    def verify(self, archive_path: str) -> None:
        logger.info("Verifying archive '%s'", archive_path)

        try:
            with tarfile.open(archive_path, mode = "r"):
                pass
        except tarfile.TarError as exception:
            raise RuntimeError("Archive '%s' is corrupted" % archive_path) from exception


    def _extract_implementation(self, archive_path: str, extraction_directory: str, file_collection: List[str], *, simulate: bool = False) -> None:
        logger.debug("Extracting files to '%s'", extraction_directory)

        with tarfile.open(archive_path, mode = "r") as archive_file:
            for source in file_collection:
                destination = os.path.normpath(os.path.join(extraction_directory, source))
                logger.debug("+ '%s' => '%s'", source, destination)
                if not simulate:
                    archive_file.extract(source, extraction_directory)
