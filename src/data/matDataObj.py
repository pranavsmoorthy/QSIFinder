class matDataObj:
    def __init__(self, formula, bandGap, hullDistance, formationEnergy, thickness, symmetry):
        self.formula = formula
        self.bandGap = bandGap
        self.hullDistance = hullDistance
        self.formationEnergy = formationEnergy
        self.thickness = thickness
        self.symmetry = symmetry

    def __str__(self):
        return f"matDataObj(\n    formula={self.formula},\n    bandGap={self.bandGap},\n    hullDistance={self.hullDistance},\n    formationEnergy={self.formationEnergy},\n    thickness={self.thickness},\n    symmetry={self.symmetry}\n)"
