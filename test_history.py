import os
import pathlib
import unittest

from numpy import datetime64
from pandas._libs.tslibs.timestamps import Timestamp

import history
from dfreader import read_df


class MyTestCase(unittest.TestCase):
    def test_something(self):
        df = read_df(self.testdata_dir() / "status_testdata.csv")
        x = history.calc_history(df)
        self.assertIn( Timestamp('2021-01-18 00:00:00'), x)

    def test_week_on_sunday(self):
        df = read_df(self.testdata_dir() / "testdata_full_week.csv")
        x = history.calc_history(df)
        self.assertIn( Timestamp('2021-02-01 00:00:00'), x)

    def testdata_dir(self):
        return pathlib.Path(os.path.dirname(__file__)) / "testdata"


if __name__ == '__main__':
    unittest.main()
