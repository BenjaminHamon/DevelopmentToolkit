import asyncio
from typing import Any


def from_result(value: Any) -> asyncio.Future:
    future = asyncio.Future()
    future.set_result(value)
    return future
