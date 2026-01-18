import unittest

class TestMath(unittest.TestCase):
    def testBandGapSubindex(self):
        from utils.debug import logDebug
        from indexCalc import getBandGapSubscore

        logDebug(str(getBandGapSubscore(2)))

if __name__ == '__main__':
    unittest.main()