import sys
import os

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
    
    if finalCandidate.formula is None:
        return {'index': None, 'sub_scores': None, 'error': "No valid material candidate found in MP or OQMD databases."}
    
    log_debug(finalCandidate)

    result = ic.getTotalIndex(finalCandidate, weights)
    return {'index': result['index'], 'sub_scores': result['sub_scores'], 'error': None}
