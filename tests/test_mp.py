import unittest

formula = "FeS2"

class TestMP(unittest.TestCase):
    def test_mp_retrieval(self):
        import data.mp as mp
        import json

        print(json.dumps(mp.retrieveMPData(formula), indent=4))

    def test_mp_cleaning(self):
        import data.mp as mp
        from utils.debug import log_debug

        data = mp.retrieveMPData(formula)
        filteredData = mp.filter(data)

        log_debug(str(filteredData))

if __name__ == '__main__':
    unittest.main()