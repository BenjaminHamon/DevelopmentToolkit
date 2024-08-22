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
from bhamon_development_toolkit.processes.process_output_collector import ProcessOutputCollector
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner


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


@pytest.mark.asyncio
async def test_output_timeout():
    spawner = ProcessSpawner(is_console = True)
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "import time; print('before'); time.sleep(10); print('after')" ])

    options = ProcessOptions(
        output_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    watcher = await spawner.spawn_process(command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    if options.output_timeout is None:
        raise RuntimeError("Output timeout should not be none")

    await asyncio.wait_for(watcher.wait(), timeout = (options.output_timeout + datetime.timedelta(seconds = 0.5)).total_seconds())

    with pytest.raises(ProcessTimeoutException) as exception:
        await watcher.complete()
    assert exception.value.exit_code == get_expected_termination_exit_code()

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == get_expected_termination_exit_code()


@pytest.mark.asyncio
async def test_output():
    spawner = ProcessSpawner(is_console = True)
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "print('hello')" ])

    options = ProcessOptions(
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    watcher = await spawner.spawn_process(command = command, options = options)

    output_collector = ProcessOutputCollector()
    watcher.add_output_handler(output_collector)

    await watcher.start()
    await watcher.wait()
    await watcher.complete()

    status = watcher.get_status()

    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 0

    assert output_collector.get_stdout() == "hello\n"
    assert output_collector.get_stderr() == ""


@pytest.mark.asyncio
async def test_output_stderr():
    spawner = ProcessSpawner(is_console = True)
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "import sys; print('hello stderr', file = sys.stderr)" ])

    options = ProcessOptions(
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    watcher = await spawner.spawn_process(command = command, options = options)

    output_collector = ProcessOutputCollector()
    watcher.add_output_handler(output_collector)

    await watcher.start()
    await watcher.wait()
    await watcher.complete()

    status = watcher.get_status()

    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 0

    assert output_collector.get_stdout() == ""
    assert output_collector.get_stderr() == "hello stderr\n"


@pytest.mark.asyncio
async def test_output_unicode():
    spawner = ProcessSpawner(is_console = True)
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "print('… é ² √ 👍')" ])

    options = ProcessOptions(
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    watcher = await spawner.spawn_process(command = command, options = options)

    output_collector = ProcessOutputCollector()
    watcher.add_output_handler(output_collector)

    await watcher.start()
    await watcher.wait()
    await watcher.complete()

    status = watcher.get_status()

    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 0

    assert output_collector.get_stdout() == "… é ² √ 👍\n"
    assert output_collector.get_stderr() == ""
