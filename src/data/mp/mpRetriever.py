import os
from mp_api.client import MPRester
from dotenv import load_dotenv

load_dotenv()
MP_KEY = os.getenv("MP_KEY")

def retrieveMPData(formula):
    with MPRester(MP_KEY) as mpr:
        docs = mpr.materials.summary.search(
            formula=formula,
            fields=[
                "material_id", 
                "deprecated",
                "formula_pretty",
                "band_gap", 
                "energy_above_hull",
                "formation_energy_per_atom",
                "structure", #Thickness at structure -> lattice -> c
                "symmetry", #Number -> number
                #Prototype still needs to be done
            ],
        )
        
        data = []

        if len(docs) != 0:
            for d in docs:
                data.append({
                    "id": d.material_id,
                    "deprecated": d.deprecated,
                    "formula": d.formula_pretty,
                    "bandGap": d.band_gap,
                    "hullDistance": d.energy_above_hull,
                    "formationEnergy": d.formation_energy_per_atom,
                    "thickness": d.structure.lattice.c,
                    "symmetry": d.symmetry.number,
                    "prototype": "Not implemented",
                    "dataFound": True
                })
        else:
            data.append({
                "message": "No data found in MP, switching to OQMD",
                "dataFound": False
            })

        return data