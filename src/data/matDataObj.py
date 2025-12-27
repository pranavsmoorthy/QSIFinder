class matDataObj:
    def __init__(self, formula, bandGap, hullDistance, formationEnergy, thickness, symmetry):
        self.formula = formula
        self.bandGap = bandGap
        self.hullDistance = hullDistance
        self.formationEnergy = formationEnergy
        self.thickness = thickness
        self.symmetry = symmetry

    @classmethod
    def materialNotFound(cls):
        return cls(
            formula=None,
            bandGap=None,
            hullDistance=None,
            formationEnergy=None,
            thickness=None,
            symmetry=None
        )

    def __str__(self):
        return f"""matDataObj(    
        \033[1mformula=\033[0m {self.formula}    
        \033[1mbandGap=\033[0m {self.bandGap}    
        \033[1mhullDistance=\033[0m {self.hullDistance}    
        \033[1mformationEnergy=\033[0m {self.formationEnergy}    
        \033[1mthickness=\033[0m {self.thickness}    
        \033[1msymmetry=\033[0m {self.symmetry}
    )"""
