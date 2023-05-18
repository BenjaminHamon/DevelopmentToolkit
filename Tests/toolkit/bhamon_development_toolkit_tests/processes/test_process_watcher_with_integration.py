""" Integration tests for ProcessWatcher """

import asyncio
import datetime
import platform
import signal

import pytest

from bhamon_development_toolkit.processes.exceptions.process_failure_exception import ProcessFailureException
from bhamon_development_toolkit.processes.exceptions.process_timeout_exception import ProcessTimeoutException
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner


@pytest.fixture
def event_loop():
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy()) # pylint: disable = no-member

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def get_expected_termination_exit_code() -> int:
    if platform.system() == "Windows":
        return 0xC000013A # STATUS_CONTROL_C_EXIT
    return - signal.SIGTERM


@pytest.mark.asyncio
async def test_run_success():
    spawner = ProcessSpawner(is_console = True)
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "pass" ])

    options = ProcessOptions(
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    watcher = await spawner.spawn_process(command = command, options = options)

    await watcher.start()
    await watcher.wait()
    await watcher.complete()

    status = watcher.get_status()

    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 0


@pytest.mark.asyncio
async def test_run_failure():
    spawner = ProcessSpawner(is_console = True)
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "raise RuntimeError" ])

    options = ProcessOptions(
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    watcher = await spawner.spawn_process(command = command, options = options)

    await watcher.start()
    await watcher.wait()

    with pytest.raises(ProcessFailureException) as exception:
        await watcher.complete()
    assert exception.value.exit_code == 1

    status = watcher.get_status()

    assert status.executable_name == "python"
    assert status.executable_path == "python"
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 1


@pytest.mark.asyncio
async def test_terminate():
    spawner = ProcessSpawner(is_console = True)
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "import time; time.sleep(10)" ])

    options = ProcessOptions(
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    watcher = await spawner.spawn_process(command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    await asyncio.sleep(0.1)

    await watcher.terminate("Interrupt")

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == get_expected_termination_exit_code()


@pytest.mark.asyncio
async def test_run_timeout():
    spawner = ProcessSpawner(is_console = True)
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "import time; time.sleep(10)" ])

    options = ProcessOptions(
        run_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    watcher = await spawner.spawn_process(command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    if options.run_timeout is None:
        raise RuntimeError("Run timeout should not be none")

    await asyncio.wait_for(watcher.wait(), timeout = (options.run_timeout + datetime.timedelta(seconds = 0.5)).total_seconds())

    with pytest.raises(ProcessTimeoutException) as exception:
        await watcher.complete()
    assert exception.value.exit_code == get_expected_termination_exit_code()

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == get_expected_termination_exit_code()


# @pytest.mark.asyncio
# async def test_output_timeout():
#     termination_exit_code = - signal.SIGTERM
#     if platform.system() == "Windows":
#         termination_exit_code = 0xC000013A # STATUS_CONTROL_C_EXIT

#     process_watcher_instance = ProcessWatcher(is_console = True)
#     process_watcher_instance.output_timeout = 1

#     await process_watcher_instance.start([ "python", "-c", "import time; time.sleep(10)" ])

#     assert process_watcher_instance.process is not None
#     assert process_watcher_instance.process.returncode is None
#     assert process_watcher_instance.is_running()

#     await asyncio.wait_for(process_watcher_instance.wait(), timeout = process_watcher_instance.output_timeout + 1)

#     assert process_watcher_instance.process is not None
#     assert process_watcher_instance.process.returncode == termination_exit_code
#     assert not process_watcher_instance.is_running()


# @pytest.mark.asyncio
# async def test_output():

#     process_watcher_instance = ProcessWatcher(is_console = True)
#     stream = process_watcher_instance.add_stream_reader()

#     await process_watcher_instance.run([ "python", "-c", "print('hello')" ])

#     output = (await stream.read()).decode("utf-8").rstrip()
#     assert output == "hello"


# @pytest.mark.asyncio
# async def test_output_unicode():

#     process_watcher_instance = ProcessWatcher(is_console = True)
#     stream = process_watcher_instance.add_stream_reader()

#     await process_watcher_instance.run([ "python", "-c", "print('… é ² √ 👍')" ])

#     output = (await stream.read()).decode("utf-8").rstrip()
#     assert output == "… é ² √ 👍"
