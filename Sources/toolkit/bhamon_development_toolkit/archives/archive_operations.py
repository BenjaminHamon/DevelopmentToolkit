import abc
import logging
from typing import List, Optional, Tuple


logger = logging.getLogger("ArchiveOperations")


class ArchiveOperations(abc.ABC):


    @abc.abstractmethod
    def get_file_extension(self) -> str:
        """ Get the archive file extension """


    @abc.abstractmethod
    def create(self, archive_path: str, mapping_collection: List[Tuple[str,str]], *, simulate: bool = False) -> None:
        """ Create an archive with mappings of path sources and destinations """


    @abc.abstractmethod
    def list_files(self, archive_path: str)-> List[str]:
        """ List the files from an archive """


    @abc.abstractmethod
    def verify(self, archive_path: str) -> None:
        """ Verify the integrity of an archive """


    @abc.abstractmethod
    def extract(self, # pylint: disable = too-many-arguments
            archive_path: str, output_directory: str,
            extraction_directory: Optional[str] = None,
            file_collection: Optional[List[str]] = None,
            replace: bool = False, simulate: bool = False) -> None:
        """ Extract an archive to the provided output directory """
