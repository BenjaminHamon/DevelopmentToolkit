import dataclasses


@dataclasses.dataclass
class PylintScope:
    identifier: str
    path_or_module: str
