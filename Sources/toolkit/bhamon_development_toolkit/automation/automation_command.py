import abc
import argparse


class AutomationCommand(abc.ABC):


    @abc.abstractmethod
    def configure_argument_parser(self, subparsers: argparse._SubParsersAction, **kwargs) -> argparse.ArgumentParser: # pylint: disable = protected-access
        pass


    @abc.abstractmethod
    def check_requirements(self, arguments: argparse.Namespace, **kwargs) -> None:
        pass


    @abc.abstractmethod
    def run(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        pass


    @abc.abstractmethod
    async def run_async(self, arguments: argparse.Namespace, simulate: bool, **kwargs) -> None:
        pass
