import dataclasses
import datetime
from typing import Optional


@dataclasses.dataclass(frozen = True)
class PythonPackageMetadata:
    product_identifier: Optional[str] = None
    version_identifier: Optional[str] = None
    revision_date: Optional[datetime.datetime] = None
    copyright_text: Optional[str] = None

    @property
    def revision_date_as_string(self) -> Optional[str]:
        if self.revision_date is None:
            return None

        return self.revision_date.replace(tzinfo = None).isoformat() + "Z"
