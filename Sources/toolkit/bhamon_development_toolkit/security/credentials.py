import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen = True)
class Credentials:
    username: Optional[str]
    secret: Optional[str]
