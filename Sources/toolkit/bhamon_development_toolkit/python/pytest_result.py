
import dataclasses


@dataclasses.dataclass(frozen = True)
class PytestResult:
    identifier: str
    status: str
