""" Unit tests for ProcessWatcher """

import asyncio
import datetime
from bhamon_development_toolkit.processes.process_output_collector import ProcessOutputCollector

import pytest

from bhamon_development_toolkit.processes.exceptions.process_failure_exception import ProcessFailureException
from bhamon_development_toolkit.processes.exceptions.process_timeout_exception import ProcessTimeoutException
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_watcher import ProcessWatcher

from .fake_process import FakeProcess


@pytest.mark.asyncio
async def test_run_success():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 0.5))
    watcher = ProcessWatcher(process, command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    await watcher.wait()

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 0

    await watcher.complete()

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 0


@pytest.mark.asyncio
async def test_run_failure():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 0.5), exit_code_for_normal_completion = 1)
    watcher = ProcessWatcher(process, command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    await watcher.wait()

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 1

    with pytest.raises(ProcessFailureException) as exception:
        await watcher.complete()
    assert exception.value.exit_code == 1

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 1


@pytest.mark.asyncio
async def test_terminate():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        termination_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 2))
    watcher = ProcessWatcher(process, command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    await watcher.terminate("Interrupt")

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == -1


@pytest.mark.asyncio
async def test_terminate_with_normal_completion():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        termination_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 0.5))
    watcher = ProcessWatcher(process, command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    await process.wait()

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 0

    await watcher.terminate("Interrupt")

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 0


@pytest.mark.asyncio
async def test_terminate_with_custom_exit_code():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        termination_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 2))
    watcher = ProcessWatcher(process, command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    await watcher.terminate("Interrupt", exit_code = 5)

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == 5


@pytest.mark.asyncio
async def test_terminate_force():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        termination_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 2), allow_termination = False)
    watcher = ProcessWatcher(process, command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    await watcher.terminate("Interrupt")

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == -2


@pytest.mark.asyncio
async def test_run_timeout():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        run_timeout = datetime.timedelta(seconds = 0.5),
        termination_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 2))
    watcher = ProcessWatcher(process, command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    if options.run_timeout is None:
        raise RuntimeError("Run timeout should not be none")

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(watcher.wait(), timeout = (options.run_timeout + datetime.timedelta(seconds = 0.5)).total_seconds())

    with pytest.raises(ProcessTimeoutException) as exception:
        await watcher.complete()
    assert exception.value.exit_code == -1

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == -1


@pytest.mark.asyncio
async def test_output_timeout():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        output_timeout = datetime.timedelta(seconds = 0.5),
        termination_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 2))
    watcher = ProcessWatcher(process, command, options)

    await watcher.start()

    status = watcher.get_status()
    assert status.pid > 0
    assert status.is_running
    assert status.exit_code is None

    if options.output_timeout is None:
        raise RuntimeError("Output timeout should not be none")

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(watcher.wait(), timeout = (options.output_timeout + datetime.timedelta(seconds = 0.5)).total_seconds())

    with pytest.raises(ProcessTimeoutException) as exception:
        await watcher.complete()
    assert exception.value.exit_code == -1

    status = watcher.get_status()
    assert status.pid > 0
    assert not status.is_running
    assert status.exit_code == -1


@pytest.mark.asyncio
async def test_output():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        termination_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    stdout = asyncio.StreamReader()
    stderr = asyncio.StreamReader()

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 0.5), stdout = stdout, stderr = stderr)
    watcher = ProcessWatcher(process, command, options)
    output_collector = ProcessOutputCollector()
    watcher.add_output_handler(output_collector)

    stdout.feed_data("hello stdout\n".encode(options.encoding))
    stderr.feed_data("hello stderr\n".encode(options.encoding))

    stdout.feed_data("bye stdout\n".encode(options.encoding))
    stderr.feed_data("bye stderr\n".encode(options.encoding))

    stdout.feed_eof()
    stderr.feed_eof()

    await watcher.start()
    await watcher.wait()
    await watcher.complete()

    assert output_collector.get_stdout() == "hello stdout\nbye stdout\n"
    assert output_collector.get_stderr() == "hello stderr\nbye stderr\n"


@pytest.mark.asyncio
async def test_output_unicode():
    command = ExecutableCommand("dummy")

    options = ProcessOptions(
        termination_timeout = datetime.timedelta(seconds = 0.5),
        wait_update_interval = datetime.timedelta(seconds = 0.1))

    stdout = asyncio.StreamReader()
    stderr = asyncio.StreamReader()

    process = FakeProcess(pid = 1, execution_duration = datetime.timedelta(seconds = 0.5), stdout = stdout, stderr = stderr)
    watcher = ProcessWatcher(process, command, options)
    output_collector = ProcessOutputCollector()
    watcher.add_output_handler(output_collector)

    stdout.feed_data("… é ² √ 👍\n".encode(options.encoding))
    stderr.feed_data("… é ² √ 👍\n".encode(options.encoding))

    stdout.feed_eof()
    stderr.feed_eof()

    await watcher.start()
    await watcher.wait()
    await watcher.complete()

    assert output_collector.get_stdout() == "… é ² √ 👍\n"
    assert output_collector.get_stderr() == "… é ² √ 👍\n"
