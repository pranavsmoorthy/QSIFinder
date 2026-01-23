class matDataObj:
    def __init__(self, formula, bandGap, hullDistance, formationEnergy, symmetry):
        self.formula = formula
        self.bandGap = bandGap
        self.hullDistance = hullDistance
        self.formationEnergy = formationEnergy
        self.symmetry = symmetry

    @classmethod
    def materialNotFound(cls):
        return cls(
            formula=None,
            bandGap=None,
            hullDistance=None,
            formationEnergy=None,
            symmetry=None
        )

    def __str__(self):
        return f"""matDataObj(    
        formula= {self.formula}    
        bandGap= {self.bandGap}    
        hullDistance= {self.hullDistance}    
        formationEnergy= {self.formationEnergy}    
        symmetry= {self.symmetry}
    )"""
