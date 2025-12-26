import unittest

class TestFull(unittest.TestCase):
    def test_full_comparison(self):
        import data.mp as mp
        import data.oqmd as oqmd
        from utils.debug import log_debug

        formula = "C"

        dataMP = mp.retrieveMPData(formula)
        filteredDataMP = mp.filter(dataMP)

        dataOQMD = oqmd.retrieveOQMDData(formula)
        filteredDataOQMD = oqmd.filter(dataOQMD)

        log_debug("MP Data: " + str(filteredDataMP))
        log_debug("OQMD Data: " + str(filteredDataOQMD))

if __name__ == '__main__':
    unittest.main()