import os


def is_same_file(path1: str, path2: str):
    try:
        return os.path.samefile(path1, path2)
    except FileNotFoundError:
        return False

