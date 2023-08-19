# pylint: disable = line-too-long

""" Unit tests for PylintOutputHandler """


import os

from bhamon_development_toolkit.python.pytest_output_handler import PytestOutputHandler
from bhamon_development_toolkit.python.pytest_scope import PytestScope


def test_parse_test_result():
    scope = PytestScope(identifier = "bhamon-development-toolkit", path = os.path.join("Tests", "toolkit"), filter_expression = None)
    output_handler = PytestOutputHandler(scope)

    line = "Tests/toolkit/bhamon_development_toolkit_tests/processes/test_process_watcher.py::test_run_success PASSED [  3%]"
    test_result = output_handler._parse_test_result(line) # pylint: disable = protected-access

    assert test_result is not None
    assert test_result.identifier == "bhamon_development_toolkit_tests.processes.test_process_watcher.test_run_success"
    assert test_result.status == "passed"
