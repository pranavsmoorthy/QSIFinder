import unittest

class TestOQMD(unittest.TestCase):
    def test_oqmd_retrieval(self):
        import data.oqmd as oqmd
        from utils.debug import log_debug
        import json

        log_debug(json.dumps(oqmd.retrieveOQMDData("KMgAlWS6"), indent=4))

    def test_oqmd_cleaning(self):
        import data.oqmd as oqmd
        from utils.debug import log_debug

        data = oqmd.retrieveOQMDData("C")
        filteredData = oqmd.filter(data)

        log_debug(str(filteredData))

if __name__ == '__main__':
    unittest.main()