import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.mp import mpRetriever as mp
from src.data.oqmd import oqmdRetriever as oqmd
from src.data.mp import mpCleaner
from src.data.oqmd import oqmdCleaner
from src.indexCalc import subscores as ic
from utils.debug import log_debug
from src.data.matDataObj import matDataObj

def calculate_qsi(formula, force_oqmd=False, weights=ic.weightsDefault):
    log_debug(f"Calculating QSI for {formula}...")
    dataMP = mp.retrieveMPData(formula) if not force_oqmd else [{"dataFound": False}]
    finalCandidate = None

    if dataMP[0].get("dataFound") and not force_oqmd:
        finalCandidate = mpCleaner.filter(dataMP)
    else:
        dataOQMD = oqmd.retrieveOQMDData(formula)
        finalCandidate = oqmdCleaner.filter(dataOQMD)
    
    log_debug("Final Candidate: " + str(finalCandidate))

    if finalCandidate.formula is None:
        return {'index': None, 'error': "No valid material candidate found in MP or OQMD databases."}

    log_debug("Calculating Index...")
    
    index = ic.getTotalIndex(finalCandidate, weights)
    log_debug(f"Index Calculated for {formula}: {index}")
    
    return {'index': index, 'error': None}
