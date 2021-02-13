import os
import pathlib


def data_file():
    return work_dir() / 'data.csv'


def cred_file():
    return work_dir() / "credentials.json"


def work_dir():
    return pathlib.Path( os.path.expanduser("~" ) ) / "nyt-crossword-data"