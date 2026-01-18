from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

import os
from dotenv import load_dotenv
from mp_api.client import MPRester

from utils.debug import logDebug
from data.matDataObj import matDataObj

load_dotenv()
mpKey = os.getenv("MP_KEY")


def filter(data):
    if data[0].get("dataFound"):
        logDebug("Filtering...")

        with MPRester(mpKey) as mpr:
            ids = []
            matcher = StructureMatcher()

            for i in range(len(data)):
                if(not data[i].get("deprecated")):
                    ids.append(data[i].get("mpId"))

            docs = mpr.materials.summary.search(material_ids=ids, fields=["material_id", "structure"])
            structures = []

            for doc in docs:
                struct = doc.structure
                struct.label = str(doc.material_id) 
                structures.append(struct)

            logDebug("Identifying and grouping dupes...")
            groups = matcher.group_structures(structures)

            sortedGroups = []

            logDebug(f"Found these many unique results from MP: {len(groups)}")
            logDebug("Sorting groups of duplicates...")
            for group in groups:
                subgroup = []

                for entry in group:
                    correspondingDataPoint = [d for d in data if d.get("mpId") == entry.label]
                    subgroup.append(correspondingDataPoint)
                
                sortedSubgroup = sorted(subgroup, key=lambda x: (x[0]['hullDistance'], abs(x[0]['bandGap'] - 1)))
                sortedGroups.append(sortedSubgroup)

            finalizedCandidates = []

            logDebug("Finalizing candidates...")
            for group in sortedGroups:
                finalizedCandidates.append(group[0])

            finalizedSorted = sorted(finalizedCandidates, key=lambda x: (x[0]['hullDistance'], abs(x[0]['bandGap'] - 1)))
            final = finalizedSorted[0]

            logDebug("Finalized MP candidate")

            return matDataObj(
                formula=final[0].get("formula"), 
                bandGap=final[0].get("bandGap"), 
                hullDistance=final[0].get("hullDistance"), 
                formationEnergy=final[0].get("formationEnergy"), 
                thickness=final[0].get("thickness")/10, 
                symmetry=final[0].get("symmetry")
            )
    else:
        return matDataObj.materialNotFound()