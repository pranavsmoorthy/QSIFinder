import json
import os
import sys

projectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, projectRoot)

from indexCalc.calculator import calculateQsi
from src.bulkTest.confusionMatrixUi import ConfusionMatrixWindow
from utils.debug import logDebug

def runBulkTest(inputFilePath, outputDir, threshold=0.7, progressCallback=None):
    logDebug(f"Starting bulk test with input file: {inputFilePath}")
    try:
        with open(inputFilePath, 'r') as f:
            materials = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logDebug(f"Error reading input file: {e}")
        return None

    chunkSize = 50
    materialItems = list(materials.items())
    totalMaterials = len(materialItems)
    
    truePositives = {}
    trueNegatives = {}
    falsePositives = {}
    falseNegatives = {}
    inconclusiveMaterials = []

    for i in range(0, totalMaterials, chunkSize):
        chunk = materialItems[i:i+chunkSize]
        
        for processedCount, (formula, isTrulySuitable) in enumerate(chunk, start=i):
            logDebug(f"Processing {formula} ({processedCount + 1}/{totalMaterials})")
            
            if progressCallback:
                progressCallback(processedCount + 1, totalMaterials, formula)

            result = calculateQsi(formula)
            
            if result.get('error'):
                logDebug(f"Could not process {formula}: {result['error']}")
                if formula not in inconclusiveMaterials: inconclusiveMaterials.append(formula)
                continue

            qsi = result['index']
            if qsi is None:
                if formula not in inconclusiveMaterials: inconclusiveMaterials.append(formula)
                continue

            isPredictedSuitable = qsi >= threshold

            if isTrulySuitable and isPredictedSuitable:
                truePositives[formula] = qsi
            elif not isTrulySuitable and not isPredictedSuitable:
                trueNegatives[formula] = qsi
            elif not isTrulySuitable and isPredictedSuitable:
                falsePositives[formula] = qsi
            elif isTrulySuitable and not isPredictedSuitable:
                falseNegatives[formula] = qsi
        
        writeChunkResults(outputDir, truePositives, trueNegatives, falsePositives, falseNegatives, inconclusiveMaterials)

    logDebug(f"Bulk test finished. Results saved in '{outputDir}' directory.")
    
    return (len(truePositives), len(trueNegatives), len(falsePositives), len(falseNegatives), len(inconclusiveMaterials))

def writeChunkResults(outputDir, tp, tn, fp, fn, inconclusive):
    with open(os.path.join(outputDir, 'truePositives.json'), 'w') as f:
        json.dump(tp, f, indent=4)
    with open(os.path.join(outputDir, 'trueNegatives.json'), 'w') as f:
        json.dump(tn, f, indent=4)
    with open(os.path.join(outputDir, 'falsePositives.json'), 'w') as f:
        json.dump(fp, f, indent=4)
    with open(os.path.join(outputDir, 'falseNegatives.json'), 'w') as f:
        json.dump(fn, f, indent=4)
    with open(os.path.join(outputDir, 'inconclusive.json'), 'w') as f:
        json.dump(inconclusive, f, indent=4)
    