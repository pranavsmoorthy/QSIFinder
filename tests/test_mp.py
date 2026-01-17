import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

formula = "MoS2"

class TestMP(unittest.TestCase):
    def test_mp_retrieval(self):
        import src.data.mp as mp
        import json

        print(json.dumps(mp.retrieveMPData(formula), indent=4))

    def test_mp_cleaning(self):
        import src.data.mp as mp
        from src.data.matDataObj import matDataObj
        from utils.debug import log_debug

        data = mp.retrieveMPData(formula)
        filteredData = mp.filter(data)

        print(str(filteredData))

if __name__ == '__main__':
    unittest.main()