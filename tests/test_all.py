import unittest

formula = "H2O"
forceOQMD = False

class TestAll(unittest.TestCase):
    def test(self):
        import data.mp as mp
        import data.oqmd as oqmd
        import indexCalc as ic
        from utils.debug import log_debug

        dataMP = mp.retrieveMPData(formula) if not forceOQMD else [{"dataFound": False}]
        finalCandidate = None

        if dataMP[0].get("dataFound") and not forceOQMD:
            finalCandidate = mp.filter(dataMP)
        else:
            dataOQMD = oqmd.retrieveOQMDData(formula)
            finalCandidate = oqmd.filter(dataOQMD)
        
        
        log_debug("Final Candidate: " + str(finalCandidate))

        if finalCandidate.formula is None:
            log_debug("No valid material candidate found in MP or OQMD databases.")
            return

        log_debug("Calculating Index...")
        index = ic.getTotalIndex(finalCandidate)
        log_debug("Index Calculated: " + str(index))
 
if __name__ == '__main__':
    unittest.main()