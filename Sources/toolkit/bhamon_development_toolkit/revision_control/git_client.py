import datetime
import logging
import os
import subprocess
from typing import Optional

from bhamon_development_toolkit.revision_control.revision_control_client import RevisionControlClient


logger = logging.getLogger("Git")


class GitClient(RevisionControlClient):


    def __init__(self, git_executable: Optional[str] = None, working_directory: Optional[str] = None) -> None:
        self._git_executable = git_executable if git_executable is not None else "git"

        self.working_directory = working_directory if working_directory is not None else os.getcwd()
        self.encoding = "utf-8"


    def get_current_revision(self) -> str:
        return self.resolve_revision("HEAD")


    def get_current_branch(self) -> Optional[str]:
        git_command = [ self._git_executable, "branch", "--show-current" ]

        git_command_result = subprocess.run(git_command,
            check = True, capture_output = True, text = True, encoding = self.encoding, cwd = self.working_directory)

        branch = git_command_result.stdout.strip()
        return branch if not branch.isspace() else None


    def try_resolve_revision(self, reference: str) -> Optional[str]:
        try:
            return self.resolve_revision(reference)
        except subprocess.CalledProcessError:
            return None


    def resolve_revision(self, reference: str) -> str:
        git_command = [ self._git_executable, "rev-list", "--max-count", "1", reference ]

        git_command_result = subprocess.run(git_command,
            check = True, capture_output = True, text = True, encoding = self.encoding, cwd = self.working_directory)

        return git_command_result.stdout.strip()


    def get_revision_date(self, revision: str) -> datetime.datetime:
        date_as_string = self.get_revision_property(revision, "committer_date")
        return datetime.datetime.utcfromtimestamp(int(date_as_string)).replace(tzinfo = datetime.timezone.utc, microsecond = 0)


    def get_revision_property(self, revision: str, property_name: str) -> str:

        def convert_property_to_format(property_name: str) -> str: # pylint: disable = too-many-return-statements
            if property_name in [ "an", "author_name" ]:
                return "an"
            if property_name in [ "ae", "author_email" ]:
                return "ae"
            if property_name in [ "at", "author_date" ]:
                return "at"

            if property_name in [ "cn", "committer_name" ]:
                return "cn"
            if property_name in [ "ce", "committer_email" ]:
                return "ce"
            if property_name in [ "ct", "committer_date" ]:
                return "ct"

            if property_name in [ "s", "subject" ]:
                return "s"
            if property_name in [ "b", "body" ]:
                return "b"
            if property_name in [ "B", "raw_body" ]:
                return "B"

            raise ValueError("Unsupported property: '%s'" % property_name)

        git_command = [ self._git_executable, "show", "--no-patch" ]
        git_command += [ "--format=%" + convert_property_to_format(property_name), revision ]

        git_command_result = subprocess.run(git_command,
            check = True, capture_output = True, text = True, encoding = self.encoding, cwd = self.working_directory)

        return git_command_result.stdout.strip()
