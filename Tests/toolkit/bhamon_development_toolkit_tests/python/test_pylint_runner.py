""" Unit tests for PylintRunner """

import json
import os

import mockito
import pytest

from bhamon_development_toolkit.processes.executable_command import ExecutableCommand
from bhamon_development_toolkit.processes.process_options import ProcessOptions
from bhamon_development_toolkit.processes.process_runner import ProcessRunner
from bhamon_development_toolkit.processes.process_status import ProcessStatus
from bhamon_development_toolkit.python.pylint_runner import PylintRunner
from bhamon_development_toolkit.python.pylint_scope import PylintScope


@pytest.mark.asyncio
async def test_run_with_no_scopes(tmpdir):
    python_executable = "my-python"
    process_runner = mockito.mock(spec = ProcessRunner)
    pylint_runner = PylintRunner(process_runner, python_executable) # type: ignore

    all_scopes = []
    run_identifier = "my-run-identifier"
    result_directory = os.path.join(tmpdir, "LintResults")

    with pytest.raises(ValueError):
        await pylint_runner.run(all_scopes, run_identifier, result_directory)


@pytest.mark.asyncio
async def test_run_with_simulate(tmpdir):
    python_executable = "my-python"
    process_runner = mockito.mock(spec = ProcessRunner)
    pylint_runner = PylintRunner(process_runner, python_executable) # type: ignore

    all_scopes = [ PylintScope("All", "my-source-directory") ]
    result_directory = os.path.join(tmpdir, "LintResults")
    run_identifier = "my-run-identifier"

    await pylint_runner.run(all_scopes, run_identifier, result_directory, simulate = True)


@pytest.mark.asyncio
async def test_run_with_success(tmpdir):
    python_executable = "my-python"
    process_runner = mockito.mock(spec = ProcessRunner)
    pylint_runner = PylintRunner(process_runner, python_executable) # type: ignore

    async def run_as_mock(run_identifier: str, result_directory: str, scope_identifier: str) -> ProcessStatus:
        json_report_file_path = os.path.join(result_directory, run_identifier, scope_identifier + ".json")
        with open(json_report_file_path, mode = "w", encoding = "utf-8") as json_report_file:
            json.dump({}, json_report_file)

        return ProcessStatus(executable = python_executable, pid = -1, is_running = False, exit_code = 0)

    all_scopes = [ PylintScope("All", "my-source-directory") ]
    result_directory = os.path.join(tmpdir, "LintResults")
    run_identifier = "my-run-identifier"

    mockito.when(process_runner).run(mockito.any(ExecutableCommand), mockito.any(ProcessOptions), mockito.any(list), check_exit_code = False) \
        .thenReturn(run_as_mock(run_identifier, result_directory, all_scopes[0].identifier))

    await pylint_runner.run(all_scopes, run_identifier, result_directory)


@pytest.mark.asyncio
async def test_run_with_failure(tmpdir):
    python_executable = "my-python"
    process_runner = mockito.mock(spec = ProcessRunner)
    pylint_runner = PylintRunner(process_runner, python_executable) # type: ignore

    async def run_as_mock(run_identifier: str, result_directory: str, scope_identifier: str) -> ProcessStatus:
        json_report_file_path = os.path.join(result_directory, run_identifier, scope_identifier + ".json")
        with open(json_report_file_path, mode = "w", encoding = "utf-8") as json_report_file:
            json.dump({}, json_report_file)

        return ProcessStatus(executable = python_executable, pid = -1, is_running = False, exit_code = 1)

    all_scopes = [ PylintScope("All", "my-source-directory") ]
    result_directory = os.path.join(tmpdir, "LintResults")
    run_identifier = "my-run-identifier"

    mockito.when(process_runner).run(mockito.any(ExecutableCommand), mockito.any(ProcessOptions), mockito.any(list), check_exit_code = False) \
        .thenReturn(run_as_mock(run_identifier, result_directory, all_scopes[0].identifier))

    with pytest.raises(RuntimeError):
        await pylint_runner.run(all_scopes, run_identifier, result_directory)
