""" Integration tests for PylintRunner """

import os
import sys

import pytest

from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.processes.process_spawner import ProcessSpawner
from bhamon_development_toolkit.python.pylint_runner import PylintRunner
from bhamon_development_toolkit.python.pylint_scope import PylintScope


@pytest.mark.asyncio
async def test_run_with_simulate(tmpdir):
    python_executable = "my-python"
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    pylint_runner = PylintRunner(process_runner, python_executable) # type: ignore

    all_scopes = [ PylintScope("All", "my-test-directory") ]
    result_directory = os.path.join(tmpdir, "TestResults")
    run_identifier = "my-run-identifier"

    await pylint_runner.run(all_scopes, run_identifier, result_directory, simulate = True)


@pytest.mark.asyncio
async def test_run_with_success(tmpdir):
    python_executable = sys.executable
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    pylint_runner = PylintRunner(process_runner, python_executable) # type: ignore

    source_directory = os.path.join(tmpdir, "Sources")

    os.makedirs(source_directory)
    with open(os.path.join(source_directory, "my_module.py"), mode = "w", encoding = "utf-8") as source_file:
        source_file.write("\"\"\"Sample module\"\"\"\n")

    all_scopes = [ PylintScope("All", "Sources") ]
    run_identifier = "my-run-identifier"
    result_directory = os.path.join(tmpdir, "LintResults")
    working_directory = str(tmpdir)

    await pylint_runner.run(all_scopes, run_identifier, result_directory, working_directory)


@pytest.mark.asyncio
async def test_run_with_failure(tmpdir):
    python_executable = sys.executable
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    pylint_runner = PylintRunner(process_runner, python_executable) # type: ignore

    source_directory = os.path.join(tmpdir, "Sources")

    os.makedirs(source_directory)
    with open(os.path.join(source_directory, "my_module.py"), mode = "w", encoding = "utf-8") as source_file:
        source_file.write("def my_function():\n    do_nothing()\n")

    all_scopes = [ PylintScope("All", "Sources") ]
    run_identifier = "my-run-identifier"
    result_directory = os.path.join(tmpdir, "LintResults")
    working_directory = str(tmpdir)

    with pytest.raises(RuntimeError):
        await pylint_runner.run(all_scopes, run_identifier, result_directory, working_directory)


@pytest.mark.asyncio
async def test_run_with_no_tests(tmpdir):
    python_executable = sys.executable
    process_runner = ProcessRunner(ProcessSpawner(is_console = True))
    pylint_runner = PylintRunner(process_runner, python_executable) # type: ignore

    source_directory = os.path.join(tmpdir, "Sources")

    os.makedirs(source_directory)

    all_scopes = [ PylintScope("All", "Sources") ]
    run_identifier = "my-run-identifier"
    result_directory = os.path.join(tmpdir, "LintResults")
    working_directory = str(tmpdir)

    await pylint_runner.run(all_scopes, run_identifier, result_directory, working_directory)
