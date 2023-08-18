import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen = True)
class PythonPackage:
    identifier: str
    path_to_sources: str
    path_to_tests: Optional[str]

    @property
    def name_for_file_system(self):
        return self.identifier.replace("-", "_")

    @property
    def name_for_module_import(self):
        return self.identifier.replace("-", "_")
