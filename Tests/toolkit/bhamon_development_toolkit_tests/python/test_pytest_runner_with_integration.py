""" Integration tests for PytestRunner """

import asyncio
import os
import platform
import sys

import pytest

from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner
from bhamon_development_toolkit.python.pytest_runner import PytestRunner
from bhamon_development_toolkit.python.pytest_scope import PytestScope


@pytest.fixture
def event_loop():
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy()) # pylint: disable = no-member

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_run_with_simulate(tmpdir):
    python_executable = "my-python"
    process_runner = ProcessRunner(ProcessSpawner())
    pytest_runner = PytestRunner(process_runner, python_executable) # type: ignore

    all_scopes = [ PytestScope("All", "my-test-directory", None) ]
    result_directory = os.path.join(tmpdir, "TestResults")
    run_identifier = "my-run-identifier"

    await pytest_runner.run(all_scopes, run_identifier, result_directory, simulate = True)


@pytest.mark.asyncio
async def test_run_with_success(tmpdir):
    python_executable = sys.executable
    process_runner = ProcessRunner(ProcessSpawner())
    pytest_runner = PytestRunner(process_runner, python_executable) # type: ignore

    test_directory = os.path.join(tmpdir, "Tests")

    os.makedirs(test_directory)
    with open(os.path.join(test_directory, "test_my_module.py"), mode = "w", encoding = "utf-8") as test_file:
        test_file.write("def test_success():\n    pass\n")

    all_scopes = [ PytestScope("All", "Tests", None) ]
    run_identifier = "my-run-identifier"
    result_directory = os.path.join(tmpdir, "TestResults")
    working_directory = str(tmpdir)

    await pytest_runner.run(all_scopes, run_identifier, result_directory, working_directory)


@pytest.mark.asyncio
async def test_run_with_failure(tmpdir):
    python_executable = sys.executable
    process_runner = ProcessRunner(ProcessSpawner())
    pytest_runner = PytestRunner(process_runner, python_executable) # type: ignore

    test_directory = os.path.join(tmpdir, "Tests")

    os.makedirs(test_directory)
    with open(os.path.join(test_directory, "test_my_module.py"), mode = "w", encoding = "utf-8") as test_file:
        test_file.write("def test_failure():\n    raise RuntimeError\n")

    all_scopes = [ PytestScope("All", "Tests", None) ]
    run_identifier = "my-run-identifier"
    result_directory = os.path.join(tmpdir, "TestResults")
    working_directory = str(tmpdir)

    with pytest.raises(RuntimeError):
        await pytest_runner.run(all_scopes, run_identifier, result_directory, working_directory)


@pytest.mark.asyncio
async def test_run_with_no_tests(tmpdir):
    python_executable = sys.executable
    process_runner = ProcessRunner(ProcessSpawner())
    pytest_runner = PytestRunner(process_runner, python_executable) # type: ignore

    test_directory = os.path.join(tmpdir, "Tests")

    os.makedirs(test_directory)

    all_scopes = [ PytestScope("All", "Tests", None) ]
    run_identifier = "my-run-identifier"
    result_directory = os.path.join(tmpdir, "TestResults")
    working_directory = str(tmpdir)

    await pytest_runner.run(all_scopes, run_identifier, result_directory, working_directory)
