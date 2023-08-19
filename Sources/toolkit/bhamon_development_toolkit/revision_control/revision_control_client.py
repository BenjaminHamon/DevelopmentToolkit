import abc
import datetime
from typing import Optional


class RevisionControlClient(abc.ABC):


    @abc.abstractmethod
    def get_current_revision(self) -> str:
        pass


    @abc.abstractmethod
    def get_current_branch(self) -> Optional[str]:
        pass


    @abc.abstractmethod
    def try_resolve_revision(self, reference: str) -> Optional[str]:
        pass


    @abc.abstractmethod
    def resolve_revision(self, reference: str) -> str:
        pass


    @abc.abstractmethod
    def get_revision_date(self, revision: str) -> datetime.datetime:
        pass
