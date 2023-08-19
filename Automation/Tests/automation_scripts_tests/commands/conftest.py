import asyncio
import platform

import pytest


@pytest.fixture
def event_loop():
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy()) # pylint: disable = no-member

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
