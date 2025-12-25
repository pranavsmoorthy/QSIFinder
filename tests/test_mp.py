import unittest

class TestMP(unittest.TestCase):
    def test_mp_retrieval(self):
        import data.mp as mp
        import json

        print(json.dumps(mp.retrieveMPData("FeS2"), indent=4))

    def test_mp_cleaning(self):
        import data.mp as mp
        import json

        data = mp.retrieveMPData("KMgAlWS6")
        filteredData = mp.filter(data)

        print(json.dumps(filteredData, indent=4))

if __name__ == '__main__':
    unittest.main()