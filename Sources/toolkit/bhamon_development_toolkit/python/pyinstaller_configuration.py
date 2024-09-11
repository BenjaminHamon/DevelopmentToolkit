import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen = True)
class PyInstallerConfiguration:
    application_source_file_path: str
    executable_name: str
    single_file: bool = False
    windows_version_info_file_path: Optional[str] = None
