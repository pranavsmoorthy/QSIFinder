import unittest

class TestMath(unittest.TestCase):
    def test_band_gap_subindex(self):
        from utils.debug import log_debug
        from indexCalc import getBandGapSubscore

        log_debug(str(getBandGapSubscore(2)))

if __name__ == '__main__':
    unittest.main()