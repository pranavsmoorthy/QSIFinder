from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

import os
from dotenv import load_dotenv
from mp_api.client import MPRester

from utils.debug import log_debug

load_dotenv()
MP_KEY = os.getenv("MP_KEY")


def filter(data):
    if data[0].get("dataFound"):
        log_debug("Filtering...")

        with MPRester(MP_KEY) as mpr:
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

            log_debug("Identifying and grouping dupes...")
            groups = matcher.group_structures(structures)

            sortedGroups = []

            log_debug(f"Found these many unique results from MP: {len(groups)}")
            log_debug("Sorting groups of duplicates...")
            for group in groups:
                subgroup = []

                for entry in group:
                    correspondingDataPoint = [d for d in data if d.get("mpId") == entry.label]
                    subgroup.append(correspondingDataPoint)
                
                sortedSubgroup = sorted(subgroup, key=lambda x: (x[0]['bandGap'], -x[0]['symmetry']))
                sortedGroups.append(sortedSubgroup)

            finalizedCandidates = []

            log_debug("Finalizing candidates...")
            for group in sortedGroups:
                finalizedCandidates.append(group[0])

            finalizedSorted = sorted(finalizedCandidates, key=lambda x: (x[0]['bandGap'], -x[0]['symmetry']))
            return finalizedSorted[0]
    else:
        return data[0]