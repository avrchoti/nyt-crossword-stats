import os
import pathlib
import unittest

import numpy
import pandas

import status
from dfreader import read_df


class TestStatus(unittest.TestCase):
    def test_something(self):
        # given
        df = read_df(self.testdata_dir() / "status_testdata.csv")

        # when
        status_dict = status.calc_status(df, numpy.datetime64("2021-02-12"))
        # then
        self.assertEqual(status_dict["today_done"], "streak")

        streaks = status_dict["streaks"]
        self.assertEqual(len(streaks), 2 )
        self.assertDictEqual(streaks[0], {"start_date" : numpy.datetime64("2021-01-14"),"end_date" : numpy.datetime64("2021-01-25"), "days" : 12})
        self.assertDictEqual(streaks[1], {"start_date" : numpy.datetime64("2021-01-27"),"end_date" : numpy.datetime64("2021-02-13"), "days" : 18})

    def testdata_dir(self):
        return pathlib.Path(os.path.dirname(__file__)) / "testdata"


if __name__ == '__main__':
    unittest.main()
