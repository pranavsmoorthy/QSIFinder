import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

formula = "InP"

class TestOQMD(unittest.TestCase):
    def test_oqmd_retrieval(self):
        import src.data.oqmd as oqmd
        from utils.debug import log_debug
        import json

        log_debug(json.dumps(oqmd.retrieveOQMDData(formula), indent=4))

    def test_oqmd_cleaning(self):
        import src.data.oqmd as oqmd
        from utils.debug import log_debug

        data = oqmd.retrieveOQMDData(formula)
        filteredData = oqmd.filter(data)

        log_debug(str(filteredData))

if __name__ == '__main__':
    unittest.main()