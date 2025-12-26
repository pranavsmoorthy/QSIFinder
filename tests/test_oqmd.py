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
        import json

        data = oqmd.retrieveOQMDData("KMgAlWS6")
        filteredData = oqmd.filter(data)

        log_debug(str(json.dumps(filteredData, indent=4)))

if __name__ == '__main__':
    unittest.main()