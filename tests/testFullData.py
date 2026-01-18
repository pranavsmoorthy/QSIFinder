import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

formula = "FeS2"

class TestFull(unittest.TestCase):
    def testFullComparison(self):
        import src.data.mp as mp
        import src.data.oqmd as oqmd
        from utils.debug import logDebug

        dataMP = mp.retrieveMpData(formula)
        filteredDataMP = mp.filter(dataMP)

        dataOQMD = oqmd.retrieveOqmdData(formula)
        filteredDataOQMD = oqmd.filter(dataOQMD)

        logDebug("MP Data: " + str(filteredDataMP))
        logDebug("OQMD Data: " + str(filteredDataOQMD))

    def testFullFlow(self):
        import src.data.mp as mp
        import src.data.oqmd as oqmd
        from utils.debug import logDebug

        dataMP = mp.retrieveMpData(formula)
        finalCandidate = None

        if dataMP[0].get("dataFound"):
            finalCandidate = mp.filter(dataMP)
        else:
            dataOQMD = oqmd.retrieveOqmdData(formula)
            finalCandidate = oqmd.filter(dataOQMD)

        logDebug("Final Candidate: " + str(finalCandidate))

if __name__ == '__main__':
    unittest.main()