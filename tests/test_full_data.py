import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

formula = "FeS2"

class TestFull(unittest.TestCase):
    def test_full_comparison(self):
        import src.data.mp as mp
        import src.data.oqmd as oqmd
        from utils.debug import log_debug

        dataMP = mp.retrieveMPData(formula)
        filteredDataMP = mp.filter(dataMP)

        dataOQMD = oqmd.retrieveOQMDData(formula)
        filteredDataOQMD = oqmd.filter(dataOQMD)

        log_debug("MP Data: " + str(filteredDataMP))
        log_debug("OQMD Data: " + str(filteredDataOQMD))

    def test_full_flow(self):
        import src.data.mp as mp
        import src.data.oqmd as oqmd
        from utils.debug import log_debug

        dataMP = mp.retrieveMPData(formula)
        finalCandidate = None

        if dataMP[0].get("dataFound"):
            finalCandidate = mp.filter(dataMP)
        else:
            dataOQMD = oqmd.retrieveOQMDData(formula)
            finalCandidate = oqmd.filter(dataOQMD)

        log_debug("Final Candidate: " + str(finalCandidate))

if __name__ == '__main__':
    unittest.main()