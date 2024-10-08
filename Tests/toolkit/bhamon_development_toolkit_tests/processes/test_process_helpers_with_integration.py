""" Integration tests for process_helpers """

import logging

import pytest

from bhamon_development_toolkit.processes import process_helpers
from bhamon_development_toolkit.processes.exceptions.process_failure_exception import ProcessFailureException
from bhamon_development_toolkit.processes.executable_command import ExecutableCommand


def test_run_simple_success():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "pass" ])

    result = process_helpers.run_simple(logger, command)

    assert result.executable == "python"
    assert result.exit_code == 0
    assert result.standard_output == ""
    assert result.error_output == ""


def test_run_simple_failure():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "raise RuntimeError" ])

    with pytest.raises(ProcessFailureException) as exception:
        process_helpers.run_simple(logger, command)
    assert exception.value.exit_code == 1


def test_run_simple_output():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "print('hello')" ])

    result = process_helpers.run_simple(logger, command)

    assert result.executable == "python"
    assert result.exit_code == 0
    assert result.standard_output == "hello\n"
    assert result.error_output == ""


def test_run_simple_output_stderr():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "import sys; print('hello stderr', file = sys.stderr)" ])

    result = process_helpers.run_simple(logger, command)

    assert result.executable == "python"
    assert result.exit_code == 0
    assert result.standard_output == ""
    assert result.error_output == "hello stderr\n"


def test_run_simple_output_unicode():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "print('… é ² √ 👍')" ])

    result = process_helpers.run_simple(logger, command)

    assert result.executable == "python"
    assert result.exit_code == 0
    assert result.standard_output == "… é ² √ 👍\n"
    assert result.error_output == ""


@pytest.mark.asyncio
async def test_run_simple_async_success():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "pass" ])

    result = await process_helpers.run_simple_async(logger, command)

    assert result.executable == "python"
    assert result.exit_code == 0
    assert result.standard_output == ""
    assert result.error_output == ""


@pytest.mark.asyncio
async def test_run_simple_async_failure():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "raise RuntimeError" ])

    with pytest.raises(ProcessFailureException) as exception:
        await process_helpers.run_simple_async(logger, command)
    assert exception.value.exit_code == 1


@pytest.mark.asyncio
async def test_run_simple_async_output():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "print('hello')" ])

    result = await process_helpers.run_simple_async(logger, command)

    assert result.executable == "python"
    assert result.exit_code == 0
    assert result.standard_output == "hello\n"
    assert result.error_output == ""


@pytest.mark.asyncio
async def test_run_simple_async_output_stderr():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "import sys; print('hello stderr', file = sys.stderr)" ])

    result = await process_helpers.run_simple_async(logger, command)

    assert result.executable == "python"
    assert result.exit_code == 0
    assert result.standard_output == ""
    assert result.error_output == "hello stderr\n"


@pytest.mark.asyncio
async def test_run_simple_async_output_unicode():
    logger = logging.getLogger("Subprocess")
    command = ExecutableCommand("python")
    command.add_arguments([ "-c", "print('… é ² √ 👍')" ])

    result = await process_helpers.run_simple_async(logger, command)

    assert result.executable == "python"
    assert result.exit_code == 0
    assert result.standard_output == "… é ² √ 👍\n"
    assert result.error_output == ""
