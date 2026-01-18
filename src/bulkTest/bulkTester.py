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
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logDebug(f"Error reading input file: {e}")
        return None

    isValidationMode = isinstance(data, dict)
    isPredictionMode = isinstance(data, list)

    if not isValidationMode and not isPredictionMode:
        logDebug(f"Error: Input file must be a JSON object (for validation) or a JSON array of formulas (for prediction).")
        return None

    materialItemsToProcess = []
    inconclusiveMaterials = []

    if isValidationMode:
        for formula, isTrulySuitable in data.items():
            if isinstance(isTrulySuitable, bool):
                materialItemsToProcess.append((formula, isTrulySuitable))
            else:
                logDebug(f"Invalid format for '{formula}': value must be a boolean. Adding to inconclusive.")
                inconclusiveMaterials.append(formula)
    else: 
        for i, item in enumerate(data):
            if isinstance(item, str):
                materialItemsToProcess.append((item, None))
            else:
                logDebug(f"Invalid item in array at index {i}: not a string formula. Adding to inconclusive.")
                inconclusiveMaterials.append(str(item))

    if not materialItemsToProcess and not inconclusiveMaterials:
        logDebug("No materials found to process.")
        return None

    chunkSize = 50
    totalMaterials = len(materialItemsToProcess)
    
    allIndices = {}
    truePositives, trueNegatives, falsePositives, falseNegatives = {}, {}, {}, {}

    for i in range(0, totalMaterials, chunkSize):
        chunk = materialItemsToProcess[i:i+chunkSize]
        
        for processedCount, (formula, isTrulySuitable) in enumerate(chunk, start=i):
            logDebug(f"Processing {formula} ({processedCount + 1}/{totalMaterials})")
            if progressCallback:
                progressCallback(processedCount + 1, totalMaterials, formula)

            result = calculateQsi(formula)
            
            if result.get('error') or result.get('index') is None:
                logDebug(f"Could not process {formula}: {result.get('error', 'QSI is None')}")
                if formula not in inconclusiveMaterials:
                    inconclusiveMaterials.append(formula)
                continue

            qsi = result['index']
            allIndices[formula] = qsi

            if isValidationMode:
                isPredictedSuitable = qsi >= threshold
                if isTrulySuitable and isPredictedSuitable:
                    truePositives[formula] = qsi
                elif not isTrulySuitable and not isPredictedSuitable:
                    trueNegatives[formula] = qsi
                elif not isTrulySuitable and isPredictedSuitable:
                    falsePositives[formula] = qsi
                elif isTrulySuitable and not isPredictedSuitable:
                    falseNegatives[formula] = qsi
        
        writeChunkResults(outputDir, isValidationMode, allIndices,
                             truePositives, trueNegatives, falsePositives, falseNegatives,
                             inconclusiveMaterials)

    logDebug(f"Bulk test finished. Results saved in '{outputDir}' directory.")
    
    if isValidationMode:
        return ('validation', (len(truePositives), len(trueNegatives), len(falsePositives), len(falseNegatives), len(allIndices), len(inconclusiveMaterials)))
    else:
        return ('prediction', (len(allIndices), len(inconclusiveMaterials)))

def writeChunkResults(outputDir, isValidationMode, allIndices, tp, tn, fp, fn, inconclusive):
    with open(os.path.join(outputDir, 'indices.json'), 'w') as f:
        json.dump(allIndices, f, indent=4)
    with open(os.path.join(outputDir, 'inconclusive.json'), 'w') as f:
        json.dump(inconclusive, f, indent=4)
        
    if isValidationMode:
        with open(os.path.join(outputDir, 'truePositives.json'), 'w') as f:
            json.dump(tp, f, indent=4)
        with open(os.path.join(outputDir, 'trueNegatives.json'), 'w') as f:
            json.dump(tn, f, indent=4)
        with open(os.path.join(outputDir, 'falsePositives.json'), 'w') as f:
            json.dump(fp, f, indent=4)
        with open(os.path.join(outputDir, 'falseNegatives.json'), 'w') as f:
            json.dump(fn, f, indent=4)