import os


def resolve_repository_path(path: str) -> str:
    directory = os.path.dirname(os.path.realpath(path))

    while True:
        if os.path.isdir(os.path.join(directory, ".git")):
            return directory
        if os.path.dirname(directory) == directory:
            raise FileNotFoundError("Path '%s' is not a git repository" % path)
        directory = os.path.dirname(directory)
