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

    if not isinstance(materials, dict):
        logDebug(f"Error: Input file content is not a valid JSON object (dictionary).")
        return None

    valid_material_items = []
    initial_inconclusive_materials = []
    for formula, isTrulySuitable in materials.items():
        if isinstance(isTrulySuitable, bool):
            valid_material_items.append((formula, isTrulySuitable))
        else:
            logDebug(f"Invalid format for '{formula}': value must be a boolean (true/false), but found '{isTrulySuitable}'. Adding to inconclusive materials due to input format error.")
            initial_inconclusive_materials.append(formula)

    if not valid_material_items and not initial_inconclusive_materials:
        logDebug("No materials found in the input file after initial validation.")
        return None

    chunkSize = 50
    totalMaterials = len(valid_material_items)
    
    truePositives = {}
    trueNegatives = {}
    falsePositives = {}
    falseNegatives = {}
    inconclusiveMaterials = list(initial_inconclusive_materials)

    for i in range(0, totalMaterials, chunkSize):
        chunk = valid_material_items[i:i+chunkSize]
        
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
    