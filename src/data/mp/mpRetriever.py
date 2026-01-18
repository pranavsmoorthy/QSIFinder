import os
from mp_api.client import MPRester
from dotenv import load_dotenv
from utils.debug import logDebug, logError

import traceback;

load_dotenv()
mpKey = os.getenv("MP_KEY")

def retrieveMpData(formula):
    try:
        with MPRester(mpKey) as mpr:
            logDebug("Retrieving entries from MP...")

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
                ],
            )
            
            logDebug("Retrieved data from MP. Putting into dictionary...")

            data = []

            if len(docs) != 0:
                for d in docs:
                    data.append({
                        "mpId": d.material_id,
                        "deprecated": d.deprecated,
                        "formula": d.formula_pretty,
                        "bandGap": d.band_gap,
                        "hullDistance": d.energy_above_hull,
                        "formationEnergy": d.formation_energy_per_atom,
                        "thickness": d.structure.lattice.c,
                        "symmetry": d.symmetry.number,
                        "dataFound": True
                    })
            else:
                data.append({
                    "message": "No data found in MP, switching to OQMD",
                    "dataFound": False
                })

            logDebug(f"Found these many results from MP: {len(data) if data[0].get("dataFound") else "None"}")

            return data
    except Exception:
        logError()

        return [{
            "message": "Error occurred, most likely trying to parse the formula",
            "dataFound": False
        }]