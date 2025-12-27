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

    def test_full_flow(self):
        import data.mp as mp
        import data.oqmd as oqmd
        from utils.debug import log_debug

        formula = "CO923423843"

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