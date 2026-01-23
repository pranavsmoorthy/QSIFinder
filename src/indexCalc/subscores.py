from utils.debug import logDebug
from src.data import matDataObj

from math import e
import chemparse
import mendeleev as md

weightsDefault = {
    "magneticNoise": 0.45,
    "stability": 0.25,
    "symmetry": 0.15,
    "bandGap": 0.1,
    "formationEnergy": 0.05
}

def getMagneticNoiseSubscore(formula, penaltyFactor=2.5):
    # Fluctuations in the local magnetic field (which is 
    # perceived as noise) destroy qubits by causing 
    # dephasing, making quantum computation impossible.
    # 
    # This is a steep exponential decay that penalizes 
    # magnetic noise values even slightly above 0.  
    elementCounts = chemparse.parse_formula(formula)

    numerator = 0
    denominator = 0

    for el, number in elementCounts.items():
        element = md.element(el)
        avgNuclearSpin = 0

        for iso in element.isotopes:
            spin = iso.spin if iso.spin is not None else 0
            abundance = iso.abundance if iso.abundance is not None else 0

            avgNuclearSpin += spin * abundance
            logDebug(f"{avgNuclearSpin}")

        numerator += avgNuclearSpin * number
        denominator += number
    
    avgNuclearSpin = numerator / denominator

    return e ** (-penaltyFactor * avgNuclearSpin)

def getStabilitySubscore(stability, decayConstant=50):
    # Stability (hull distance) ideally is 0 eV/atom so
    # that the material is the most thermally stable and
    # the ideal value.
    # 
    # This creates a steep exponential decay where 0 yields
    # a subindex of 1. The decay constant is 0.05 eV 
    # since anything higher can lead to metastability. A
    # decently high value will be achieved at a hull 
    # distance between 0 and 0.05 eV
    return e ** (-stability / decayConstant)

def getSymmetrySubscore(symmetry, curvature=0.5):
    # High symmetry means that light is emitted equally in 
    # all directions, optimal for quantum computing.
    #
    # This gives a linear mapping with a bias where there
    # are diminishing returns for each increase in symmetry
    return (symmetry / 230) ** curvature

def getBandGapSubscore(bandGap, idealGapVisible=1.0, idealGapUV=2.5, visibleTolerance=0.5, uvTolerance=1.0, uvCutoff=2):
    # Band gap of 1.0eV is best so that effective quantum 
    # dots can be made where information can pass 
    # through easily
    #
    # This creates a bell curve centered at 1.0eV and
    # tolerance of 0.5, meaning that a material within 0.5 to
    # 1.5 eV band gap will be suitable. (Using default 
    # values)
    # 
    # If the material is determined to be a UV emitter
    # where the bandgap is greater than the cutoff, then the 
    # center and tolerance is shifted

    idealGap = idealGapVisible
    tolerance = visibleTolerance

    if bandGap > uvCutoff:
        idealGap = idealGapUV
        tolerance = uvTolerance

    return e ** (-1 * ((bandGap - idealGap) ** 2) / (2 * (tolerance ** 2)))

def getFormationEnergySubscore(formationEnergy, cutoff=0, steepness=2):
    # The formation energy should be as negative as 
    # possible since that means the most energy is absorbed
    # during formation. Highly negative values imply high
    # chemical stability.
    #
    # This creates a sigmoid function that favors negative
    # values, while being smooth enough to allow some 
    # positive and lesser negative values.
    return 1 / (1 + (e ** (steepness * (formationEnergy - cutoff))))

def getTotalIndex(data:matDataObj, weights:dict=weightsDefault):
    bandGap = data.bandGap
    stability = data.hullDistance
    formationEnergy = data.formationEnergy
    formula = data.formula
    symmetry = data.symmetry

    bgWeight = weights.get("bandGap")
    stWeight = weights.get("stability")
    feWeight = weights.get("formationEnergy")
    mnWeight = weights.get("magneticNoise")
    syWeight = weights.get("symmetry")

    bgSubscore = getBandGapSubscore(bandGap)
    stSubscore = getStabilitySubscore(stability)
    feSubscore = getFormationEnergySubscore(formationEnergy)
    mnSubscore = getMagneticNoiseSubscore(formula)
    sySubscore = getSymmetrySubscore(symmetry)

    logDebug(f"Band Gap Subscore: {bgSubscore} (Weight: {bgWeight})")
    logDebug(f"Stability Subscore: {stSubscore} (Weight: {stWeight})")
    logDebug(f"Formation Energy Subscore: {feSubscore} (Weight: {feWeight})")
    logDebug(f"Magnetic Noise Subscore: {mnSubscore} (Weight: {mnWeight})")
    logDebug(f"Symmetry Subscore: {sySubscore} (Weight: {syWeight})")

    subScores = [stSubscore, bgSubscore, feSubscore, mnSubscore, sySubscore]

    indexInfo = [
        [bgSubscore, bgWeight],
        [stSubscore, stWeight],
        [feSubscore, feWeight],
        [mnSubscore, mnWeight],
        [sySubscore, syWeight]
    ]

    index = 1

    for i in indexInfo:
        index *= (i[0] ** i[1])

    return {'index': index, 'subScores': subScores}