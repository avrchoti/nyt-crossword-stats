import pandas

import files


def read_df(filename = files.data_file()):
    df = pandas.read_csv(filename, parse_dates=["date"])
    return df