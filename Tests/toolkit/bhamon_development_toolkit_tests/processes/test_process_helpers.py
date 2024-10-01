""" Unit tests for process_helpers """

from bhamon_development_toolkit.processes import process_helpers


def test_format_executable_command():
    command = [ "my_executable", "--path", "MyDirectory/My file with spaces", "--option=value" ]
    command_formatted = process_helpers.format_executable_command(command)

    assert command_formatted == "my_executable --path 'MyDirectory/My file with spaces' --option=value"

    command = [ "my_executable", "--path", "MyDirectory/My file with spaces", "--option=value with spaces" ]
    command_formatted = process_helpers.format_executable_command(command)

    assert command_formatted == "my_executable --path 'MyDirectory/My file with spaces' '--option=value with spaces'"

    command = [ "my_executable", "--path", "MyDirectory/My file with spaces", "--option='value with spaces and quoted'" ]
    command_formatted = process_helpers.format_executable_command(command)

    assert command_formatted == "my_executable --path 'MyDirectory/My file with spaces' '--option='\"'\"'value with spaces and quoted'\"'\"''"


def test_format_executable_command_element():
    assert process_helpers.format_executable_command_element("something") == "something"
    assert process_helpers.format_executable_command_element("something with spaces") == "'something with spaces'"
    assert process_helpers.format_executable_command_element("some directory/some file") == "'some directory/some file'"
    assert process_helpers.format_executable_command_element("key=value") == "key=value"
    assert process_helpers.format_executable_command_element("key=value with spaces") == "'key=value with spaces'"
    assert process_helpers.format_executable_command_element("key='value with spaces and quoted'") == "'key='\"'\"'value with spaces and quoted'\"'\"''"
