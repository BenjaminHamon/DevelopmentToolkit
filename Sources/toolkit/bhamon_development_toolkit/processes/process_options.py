
import dataclasses
import datetime
from typing import Dict, Optional


@dataclasses.dataclass(frozen = True)
class ProcessOptions:
    working_directory: Optional[str] = None
    environment: Optional[Dict[str,str]] = None
    encoding: str = "utf-8"

    run_timeout: Optional[datetime.timedelta] = None
    output_timeout: Optional[datetime.timedelta] = None
    termination_timeout: datetime.timedelta = datetime.timedelta(seconds = 10)
    wait_update_interval: datetime.timedelta = datetime.timedelta(seconds = 1)
