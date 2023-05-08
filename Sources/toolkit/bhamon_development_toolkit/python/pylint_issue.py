
import dataclasses


@dataclasses.dataclass(frozen = True)
class PylintIssue:
    identifier: str
    code: str
    category: str
    message: str
    file_path: str
    line_in_file: int
    obj: str
