import os
import pathlib


def web_resources_root():
    return pathlib.Path(os.path.dirname(__file__))
