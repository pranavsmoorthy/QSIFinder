import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

formula = "InP"

class TestOQMD(unittest.TestCase):
    def testOqmdRetrieval(self):
        import src.data.oqmd as oqmd
        from utils.debug import logDebug
        import json

        logDebug(json.dumps(oqmd.retrieveOqmdData(formula), indent=4))

    def testOqmdCleaning(self):
        import src.data.oqmd as oqmd
        from utils.debug import logDebug

        data = oqmd.retrieveOqmdData(formula)
        filteredData = oqmd.filter(data)

        logDebug(str(filteredData))

if __name__ == '__main__':
    unittest.main()