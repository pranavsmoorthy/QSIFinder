from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.core import Structure
from pymatgen.symmetry.groups import SpaceGroup

import gemmi
import numpy as np

from data.matDataObj import matDataObj
from utils.debug import logDebug

def filter(data):
    if data[0].get("dataFound"):
        logDebug("Filtering...")

        ids = []
        structures = []
        matcher = StructureMatcher()

        logDebug("Constructing Structure Objects...")

        for d in data:
            ids.append(d.get("oqmdId"))

            lattice = d.get("structureData").get("data")[0].get("attributes").get("lattice_vectors")
            species = d.get("structureData").get("data")[0].get("attributes").get("species_at_sites")
            coords = d.get("structureData").get("data")[0].get("attributes").get("cartesian_site_positions")

            struct = Structure(lattice, species, coords, coords_are_cartesian=True)

            struct.label = d.get("oqmdId")
            structures.append(struct)

        logDebug("Sorting groups of duplicates...")
        groups = matcher.group_structures(structures)

        sortedGroups = []

        logDebug(f"Found these many unique results from OQMD: {len(groups)}")
        logDebug("Sorting groups of duplicates...")
        for group in groups:
            subgroup = []

            for entry in group:
                correspondingDataPoint = [d for d in data if d.get("oqmdId") == entry.label]

                if not type(correspondingDataPoint[0].get("symmetry")) is int:
                    sg = gemmi.find_spacegroup_by_name(correspondingDataPoint[0].get("symmetry"))
                    correspondingDataPoint[0]["symmetry"] = sg.number

                subgroup.append(correspondingDataPoint)
            
            sortedSubgroup = sorted(subgroup, key=lambda x: (x[0]['hullDistance'], (abs(x[0]['bandGap'] - 1))))
            sortedGroups.append(sortedSubgroup)

        finalizedCandidates = []

        logDebug("Finalizing candidates...")
        for group in sortedGroups:
            finalizedCandidates.append(group[0])

        finalizedSorted = sorted(finalizedCandidates, key=lambda x: (x[0]['hullDistance'], (abs(x[0]['bandGap'] - 1))))
        final = finalizedSorted[0]

        logDebug("Finalized OQMD candidate")

        return matDataObj(
            formula=final[0].get("formula"), 
            bandGap=final[0].get("bandGap"), 
            hullDistance=final[0].get("hullDistance"), 
            formationEnergy=final[0].get("formationEnergy"), 
            symmetry=final[0].get("symmetry")
        )
    else:
        return matDataObj.materialNotFound()