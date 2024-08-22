import os
import re

import pytest

from bhamon_development_toolkit.revision_control.git_direct_client import GitDirectClient


def test_branch_with_show_current(tmpdir):
    working_directory = os.path.join(str(tmpdir), "Workspace")
    git_client = GitDirectClient(working_directory = working_directory)

    os.makedirs(working_directory)
    git_client.init()

    result = git_client.branch(show_current = True)

    assert result.exit_code == 0
    assert result.standard_output is not None
    assert len(result.standard_output.splitlines()) == 1
    assert re.search(r"^[a-zA-Z0-9_\-./]+$", result.standard_output.splitlines()[0]) is not None
    assert result.error_output == ""


def test_commit(tmpdir):
    working_directory = os.path.join(str(tmpdir), "Workspace")
    git_client = GitDirectClient(working_directory = working_directory)
    git_client.configuration_options["user.name"] = "Some Author"
    git_client.configuration_options["user.email"] = "some.author@example.com"

    os.makedirs(working_directory)
    git_client.init()

    commit_message = "test_commit"
    result = git_client.commit(message = commit_message, allow_empty = True, no_edit = True)

    assert result.exit_code == 0
    assert result.standard_output is not None
    assert len(result.standard_output.splitlines()) == 1
    assert re.search(r"^\[.*?\] " + re.escape(commit_message) + r"$", result.standard_output.splitlines()[0]) is not None
    assert result.error_output == ""


def test_init(tmpdir):
    working_directory = os.path.join(str(tmpdir), "Workspace")
    git_client = GitDirectClient(working_directory = working_directory)

    assert not os.path.exists(os.path.join(working_directory, ".git"))

    with pytest.raises(NotADirectoryError):
        git_client.init()

    assert not os.path.exists(os.path.join(working_directory, ".git"))

    os.makedirs(working_directory)
    result = git_client.init()

    assert result.exit_code == 0
    assert result.standard_output is not None
    assert len(result.standard_output.splitlines()) == 1
    assert result.standard_output.splitlines()[0] \
        == "Initialized empty Git repository in %s" % (os.path.join(working_directory, ".git").replace("\\", "/") + "/")
    assert result.error_output == ""
    assert os.path.exists(os.path.join(working_directory, ".git"))


def test_rev_list(tmpdir):
    working_directory = os.path.join(str(tmpdir), "Workspace")
    git_client = GitDirectClient(working_directory = working_directory)
    git_client.configuration_options["user.name"] = "Some Author"
    git_client.configuration_options["user.email"] = "some.author@example.com"

    os.makedirs(working_directory)
    git_client.init()

    result = git_client.rev_list([ "HEAD" ])

    assert result.exit_code == 128
    assert result.standard_output == ""
    assert result.error_output is not None
    assert len(result.error_output.splitlines()) == 3
    assert result.error_output.splitlines()[0] == "fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree."

    commit_message = "test_rev_list"
    git_client.commit(message = commit_message, allow_empty = True, no_edit = True)

    result = git_client.rev_list([ "HEAD" ])

    assert result.exit_code == 0
    assert result.standard_output is not None
    assert len(result.standard_output.splitlines()) == 1
    assert re.search(r"^[0-9a-f]+$", result.standard_output.splitlines()[0]) is not None
    assert result.error_output == ""


def test_show(tmpdir):
    working_directory = os.path.join(str(tmpdir), "Workspace")
    git_client = GitDirectClient(working_directory = working_directory)
    git_client.configuration_options["user.name"] = "Some Author"
    git_client.configuration_options["user.email"] = "some.author@example.com"

    os.makedirs(working_directory)
    git_client.init()

    commit_message = "test_show"
    git_client.commit(message = commit_message, allow_empty = True, no_edit = True)

    result = git_client.show([ "HEAD" ], _format = "%an", no_patch = True)

    assert result.exit_code == 0
    assert result.standard_output is not None
    assert len(result.standard_output.splitlines()) == 1
    assert result.standard_output.splitlines()[0] == "Some Author"
    assert result.error_output == ""
