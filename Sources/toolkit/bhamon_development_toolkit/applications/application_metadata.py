import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen = True)
class ApplicationMetadata:
    product_identifier: str
    version_identifier: str
    version_identifier_full: str

    product_display_name: Optional[str] = None
    product_copyright: Optional[str] = None
    product_description: Optional[str] = None
