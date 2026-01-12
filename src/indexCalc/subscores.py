from utils.debug import log_debug
from src.data import matDataObj
from math import e

weightsDefault = {
    "stability": 0.35,
    "bandGap": 0.3,
    "formationEnergy": 0.15,
    "thickness": 0.1,
    "symmetry": 0.1
}

def getBandGapSubscore(bandGap, idealGap=1.0, tolerance=0.5):
    # Band gap of 1.5eV is best so that effective quantum 
    # dots can be made where information can pass 
    # through easily
    #
    # This creates a bell curve centered at 1.5eV and
    # tolerance of 0.5, meaning that a material within 1 to
    # 2 eV band gap will be suitable. (Using default 
    # values)
    return e ** (-1 * ((bandGap - idealGap) ** 2) / (2 * (tolerance ** 2)))

def getStabilitySubscore(stability, decayConstant=0.05):
    # Stability (hull distance) ideally is 0 eV/atom so
    # that the material is the most thermally stable and
    # the ideal value.
    # 
    # This creates a steep exponential decay where 0 yields
    # a subindex of 1. The decay constant is 0.05 eV 
    # since anything higher can lead to metastability. A
    # decently high value will be achieved at a hull 
    # distance between 0 and 0.05 eV
    return e ** (-1 * stability / decayConstant)

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

def getThicknessSubscore(thickness, idealThickness=0.6, sensitivity=0.5):
    # Thinner materials are easier to turn into dots, so a
    # lesser thickness gives a better value.
    #
    # This gives an inverse power function, where the 
    # closer the thickness is the ideal thickness, the
    # higher the score is
    return 1 / (1 + (sensitivity * ((thickness - idealThickness) ** 2)))

def getSymmetrySubscore(thickness, curvature=0.5):
    # High symmetry means that light is emitted equally in 
    # all directions, optimal for quantum computing.
    #
    # This gives a linear mapping with a bias where there
    # are diminishing returns for each increase in symmetry
    return (thickness / 230) ** curvature

def getTotalIndex(data:matDataObj, weights:dict=weightsDefault):
    bandGap = data.bandGap
    stability = data.hullDistance
    formationEnergy = data.formationEnergy
    thickness = data.thickness
    symmetry = data.symmetry

    bgWeight = weights.get("bandGap")
    stWeight = weights.get("stability")
    feWeight = weights.get("formationEnergy")
    thWeight = weights.get("thickness")
    syWeight = weights.get("symmetry")

    bgSubscore = getBandGapSubscore(bandGap)
    stSubscore = getStabilitySubscore(stability)
    feSubscore = getFormationEnergySubscore(formationEnergy)
    thSubscore = getThicknessSubscore(thickness)
    sySubscore = getSymmetrySubscore(symmetry)

    log_debug(f"Band Gap Subscore: {bgSubscore} (Weight: {bgWeight})")
    log_debug(f"Stability Subscore: {stSubscore} (Weight: {stWeight})")
    log_debug(f"Formation Energy Subscore: {feSubscore} (Weight: {feWeight})")
    log_debug(f"Thickness Subscore: {thSubscore} (Weight: {thWeight})")
    log_debug(f"Symmetry Subscore: {sySubscore} (Weight: {syWeight})")

    indexInfo = [
        [bgSubscore, bgWeight],
        [stSubscore, stWeight],
        [feSubscore, feWeight],
        [thSubscore, thWeight],
        [sySubscore, syWeight]
    ]

    index = 1

    for i in indexInfo:
        index *= (i[0] ** i[1])

    return index