from qmpy_rester import QMPYRester
from utils.debug import logDebug, logError
import subprocess

def retrieveOqmdData(formula):
    try:
        logDebug("Retrieving OQMD data...")
        with QMPYRester() as oqmdr:
            kwargs = {
                "composition": formula,  
            }

            dataFromOqmd = oqmdr.get_oqmd_phases(verbose=False, **kwargs)
            logDebug("Retrieved data from OQMD. Putting into dictionary...")
            logDebug(f"Found these many results from OQMD: {len(dataFromOqmd.get("data")) if len(dataFromOqmd.get("data")) != 0 else "None"}")


            data = []

            if len(dataFromOqmd.get("data")) != 0:
                item = 1
                for d in dataFromOqmd.get("data"):
                    logDebug("Retrieving Structure: " + (" " if item < 10 else "") + str(item) + "/" + str(len(dataFromOqmd.get("data"))))
                    item += 1

                    structKwargs = { 
                        "_oqmd_band_gap": str(d.get("band_gap")),
                        "_oqmd_stability": str(d.get("stability")),
                        "_oqmd_delta_e": str(d.get("delta_e"))
                    }

                    structureData = oqmdr.get_optimade_structures(verbose=False, **structKwargs)

                    data.append({
                        "oqmdId": d.get("entry_id"),
                        "formula": d.get("name"),
                        "bandGap": d.get("band_gap"),
                        "hullDistance": d.get("stability"),
                        "formationEnergy": d.get("delta_e"),
                        "unitCell": d.get("unit_cell"),
                        "symmetry": d.get("spacegroup"),
                        "structureData": structureData,
                        "dataFound": True
                    })
            else:
                data.append({
                    "message": "No data found in OQMD",
                    "dataFound": False
                })

            return data
    except Exception:
        logError()

        return [{
            "message": "Error occurred, most likely trying to parse the formula",
            "dataFound": False
        }]