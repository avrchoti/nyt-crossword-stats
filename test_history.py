import os
import pathlib
import unittest
import history
from dfreader import read_df


class MyTestCase(unittest.TestCase):
    def test_something(self):
        df = read_df(self.testdata_dir() / "status_testdata.csv")
        x = history.calc_history(df)

    def testdata_dir(self):
        return pathlib.Path(os.path.dirname(__file__)) / "testdata"


if __name__ == '__main__':
    unittest.main()
