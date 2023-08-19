import datetime
from typing import Optional


class ProjectVersion:


    def __init__(self, identifier: str, revision: str, revision_date: datetime.datetime, branch: Optional[str]) -> None:
        self.identifier = identifier
        self.revision = revision
        self.revision_date = revision_date
        self.branch = branch


    @property
    def revision_short(self) -> str:
        return self.revision[:10]


    @property
    def full_identifier(self) -> str:
        return self.identifier + "+" + self.revision_short
