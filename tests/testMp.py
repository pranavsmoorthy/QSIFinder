import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

formula = "MoS2"

class TestMP(unittest.TestCase):
    def testMpRetrieval(self):
        import src.data.mp as mp
        import json

        print(json.dumps(mp.retrieveMpData(formula), indent=4))

    def testMpCleaning(self):
        import src.data.mp as mp
        from src.data.matDataObj import matDataObj
        from utils.debug import logDebug

        data = mp.retrieveMpData(formula)
        filteredData = mp.filter(data)

        print(str(filteredData))

if __name__ == '__main__':
    unittest.main()