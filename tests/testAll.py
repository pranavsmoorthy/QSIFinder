import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

formula = "H2O"
forceOqmd = False

class TestAll(unittest.TestCase):
    def test(self):
        import src.data.mp as mp
        import src.data.oqmd as oqmd
        import src.indexCalc as ic
        from utils.debug import logDebug

        dataMP = mp.retrieveMpData(formula) if not forceOqmd else [{"dataFound": False}]
        finalCandidate = None

        if dataMP[0].get("dataFound") and not forceOqmd:
            finalCandidate = mp.filter(dataMP)
        else:
            dataOQMD = oqmd.retrieveOqmdData(formula)
            finalCandidate = oqmd.filter(dataOQMD)
        
        
        logDebug("Final Candidate: " + str(finalCandidate))

        if finalCandidate.formula is None:
            logDebug("No valid material candidate found in MP or OQMD databases.")
            return

        logDebug("Calculating Index...")
        index = ic.getTotalIndex(finalCandidate)
        logDebug("Index Calculated: " + str(index))
 
if __name__ == '__main__':
    unittest.main()