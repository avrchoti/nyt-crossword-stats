import os
import unittest
import pathlib
from datetime import datetime

import fetch_puzzle_stats
class MyTestCase(unittest.TestCase):

    def test_file_not_there__begin(self):
        # given

        # when
        res = fetch_puzzle_stats.read_last_date_from_file("nonexistent")

        # then
        self.assertEqual(res, fetch_puzzle_stats.BEGINNING_OF_TIME)


    def test_valid_file__returned_value(self):
        # given

        # when
        res = fetch_puzzle_stats.read_last_date_from_file(self.testdata_dir() / "test.csv")

        # then
        self.assertEqual(res, datetime(2018,1,30))

    def testdata_dir(self):
        return pathlib.Path(os.path.dirname(__file__)) / "testdata"


if __name__ == '__main__':
    unittest.main()
