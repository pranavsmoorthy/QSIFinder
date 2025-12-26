from qmpy_rester import QMPYRester
from utils.debug import log_debug, log_error
import subprocess

def retrieveOQMDData(formula):
    try:
        log_debug("Retrieving OQMD data...")
        with QMPYRester() as oqmdr:
            kwargs = {
                "composition": formula,  
            }

            dataFromOQMD = oqmdr.get_oqmd_phases(verbose=False, **kwargs)
            log_debug("Retrieved data from OQMD. Putting into dictionary...")
            log_debug(f"Found these many results from OQMD: {len(dataFromOQMD.get("data")) if len(dataFromOQMD.get("data")) != 0 else "None"}")


            data = []

            if len(dataFromOQMD.get("data")) != 0:
                item = 1
                for d in dataFromOQMD.get("data"):
                    log_debug("Retrieving Structure: " + (" " if item < 10 else "") + str(item) + "/" + str(len(dataFromOQMD.get("data"))))
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
        log_error()

        return [{
            "message": "Error occurred, most likely trying to parse the formula",
            "dataFound": False
        }]