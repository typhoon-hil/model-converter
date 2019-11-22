import os


def get_root_path():
    return os.path.split(os.path.abspath(os.path.join(
        os.path.realpath(__file__), "..", "..")))[0]
