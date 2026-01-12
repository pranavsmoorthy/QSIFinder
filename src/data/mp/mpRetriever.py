import os
from mp_api.client import MPRester
from dotenv import load_dotenv
from utils.debug import log_debug, log_error

import traceback;

load_dotenv()
MP_KEY = os.getenv("MP_KEY")

def retrieveMPData(formula):
    try:
        with MPRester(MP_KEY) as mpr:
            log_debug("Retrieving entries from MP...")

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
            
            log_debug("Retrieved data from MP. Putting into dictionary...")

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

            log_debug(f"Found these many results from MP: {len(data) if data[0].get("dataFound") else "None"}")

            return data
    except Exception:
        log_error()

        return [{
            "message": "Error occurred, most likely trying to parse the formula",
            "dataFound": False
        }]