import unittest

class TestImports(unittest.TestCase):
    def test_import_mpRetriever(self):
        import data.mp as mp
        import json

        print(json.dumps(mp.retrieveMPData("A25C384"), indent=4))

if __name__ == '__main__':
    unittest.main()