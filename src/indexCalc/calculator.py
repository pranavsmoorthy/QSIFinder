import sys
import os

from src.data.mp import mpRetriever as mp
from src.data.oqmd import oqmdRetriever as oqmd
from src.data.mp import mpCleaner
from src.data.oqmd import oqmdCleaner
from src.indexCalc import subscores as ic
from utils.debug import logDebug
from src.data.matDataObj import matDataObj

def calculateQsi(formula, forceOqmd=False, weights=ic.weightsDefault):
    logDebug(f"Calculating QSI for {formula}...")
    dataMP = mp.retrieveMpData(formula) if not forceOqmd else [{"dataFound": False}]
    finalCandidate = None

    if dataMP[0].get("dataFound") and not forceOqmd:
        finalCandidate = mpCleaner.filter(dataMP)
    else:
        dataOQMD = oqmd.retrieveOqmdData(formula)
        finalCandidate = oqmdCleaner.filter(dataOQMD)
    
    if finalCandidate.formula is None:
        return {'index': None, 'subScores': None, 'error': "No valid material candidate found in MP or OQMD databases."}
    
    logDebug(finalCandidate)

    result = ic.getTotalIndex(finalCandidate, weights)
    return {'index': result['index'], 'subScores': result['subScores'], 'error': None}
