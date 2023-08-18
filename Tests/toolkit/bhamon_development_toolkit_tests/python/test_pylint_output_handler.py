# pylint: disable = line-too-long

""" Unit tests for PylintOutputHandler """


import os

from bhamon_development_toolkit.python.pylint_output_handler import PylintOutputHandler


def test_parse_issue_message():
    output_handler = PylintOutputHandler()

    line = "sources/toolkit/bhamon_development_toolkit/__init__.py|7|bhamon_development_toolkit||Bad indentation. Found 1 spaces, expected 4|W0311|bad-indentation|warning"
    issue = output_handler._parse_issue_message(line) # pylint: disable = protected-access

    assert issue.identifier == "bad-indentation"
    assert issue.code == "W0311"
    assert issue.category == "warning"
    assert issue.message == "Bad indentation. Found 1 spaces, expected 4"
    assert issue.file_path == os.path.normpath("sources/toolkit/bhamon_development_toolkit/__init__.py")
    assert issue.line_in_file == 7
    assert issue.obj == ""
