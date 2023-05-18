import abc


class ProcessOutputHandler(abc.ABC):


    @abc.abstractmethod
    def process_stdout_line(self, line: str) -> None:
        pass


    @abc.abstractmethod
    def process_stderr_line(self, line: str) -> None:
        pass


    @abc.abstractmethod
    def process_stdout_end(self) -> None:
        pass


    @abc.abstractmethod
    def process_stderr_end(self) -> None:
        pass
