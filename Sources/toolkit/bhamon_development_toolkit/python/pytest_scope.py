import dataclasses
from typing import Optional


@dataclasses.dataclass
class PytestScope:
    identifier: str
    path: str
    filter_expression: Optional[str]
