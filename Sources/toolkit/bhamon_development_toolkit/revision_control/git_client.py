import datetime
import logging
import subprocess
from typing import Optional

from bhamon_development_toolkit.processes.exceptions.process_failure_exception import ProcessFailureException
from bhamon_development_toolkit.processes.process_result import ProcessResult
from bhamon_development_toolkit.revision_control.git_direct_client import GitDirectClient
from bhamon_development_toolkit.revision_control.revision_control_client import RevisionControlClient


logger = logging.getLogger("Git")


class GitClient(RevisionControlClient):


    def __init__(self, git_direct_client: GitDirectClient) -> None:
        self._direct_client = git_direct_client


    def get_current_revision(self) -> str:
        return self.resolve_revision("HEAD")


    def get_current_branch(self) -> Optional[str]:
        result = self._direct_client.branch(show_current = True)

        if result != 0:
            self.raise_git_exception(result)

        if result.standard_output is None:
            return None
        if result.standard_output.isspace():
            return None
        return result.standard_output.strip()


    def try_resolve_revision(self, reference: str) -> Optional[str]:
        try:
            return self.resolve_revision(reference)
        except subprocess.CalledProcessError:
            return None


    def resolve_revision(self, reference: str) -> str:
        result = self._direct_client.rev_list(commits = [ reference ], max_count = 1)

        if result != 0:
            self.raise_git_exception(result)

        if result.standard_output is None:
            return ""
        return result.standard_output.strip()


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

        result = self._direct_client.show(objects = [ revision ], _format = "%" + convert_property_to_format(property_name))

        if result != 0:
            self.raise_git_exception(result)

        if result.standard_output is None:
            return ""
        return result.standard_output.strip()


    def raise_git_exception(self, result: ProcessResult) -> None:
        exception_message = "Git command failed with exit code '%s'" % result.exit_code
        if result.error_output:
            exception_message += "\n" + result.error_output
        raise ProcessFailureException(exception_message, result.executable, result.exit_code)
