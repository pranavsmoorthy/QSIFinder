import unittest

class TestOQMD(unittest.TestCase):
    def test_oqmd_retrieval(self):
        import data.oqmd as oqmd
        import json

        print(json.dumps(oqmd.retrieveOQMDData("FeS2"), indent=4))

    def test_oqmd_cleaning(self):
        import data.oqmd as oqmd
        import json

        data = oqmd.retrieveOQMDData("FeS2")
        filteredData = oqmd.filter(data)

        print(json.dumps(filteredData, indent=4))

if __name__ == '__main__':
    unittest.main()