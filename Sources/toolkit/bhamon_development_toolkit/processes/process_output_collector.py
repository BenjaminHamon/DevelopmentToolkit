from bhamon_development_toolkit.processes.process_output_handler import ProcessOutputHandler


class ProcessOutputCollector(ProcessOutputHandler):


    def __init__(self) -> None:
        self._stdout: str = ""
        self._stderr: str = ""


    def get_stdout(self) -> str:
        return self._stdout


    def get_stderr(self) -> str:
        return self._stderr


    def process_stdout_line(self, line: str) -> None:
        self._stdout += line


    def process_stderr_line(self, line: str) -> None:
        self._stderr += line


    def process_stdout_end(self) -> None:
        pass


    def process_stderr_end(self) -> None:
        pass
