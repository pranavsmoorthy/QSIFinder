from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.core import Structure
from pymatgen.symmetry.groups import SpaceGroup

import gemmi

from utils.debug import log_debug

def filter(data):
    if data[0].get("dataFound"):
        log_debug("Filtering...")

        ids = []
        structures = []
        matcher = StructureMatcher()

        log_debug("Constructing Structure Objects...")

        for d in data:
            ids.append(d.get("oqmdId"))

            lattice = d.get("structureData").get("data")[0].get("attributes").get("lattice_vectors")
            species = d.get("structureData").get("data")[0].get("attributes").get("species_at_sites")
            coords = d.get("structureData").get("data")[0].get("attributes").get("cartesian_site_positions")

            struct = Structure(lattice, species, coords, coords_are_cartesian=True)

            struct.label = d.get("oqmdId")
            structures.append(struct)

        log_debug("Sorting groups of duplicates...")
        groups = matcher.group_structures(structures)

        sortedGroups = []

        log_debug(f"Found these many unique results from OQMD: {len(groups)}")
        log_debug("Sorting groups of duplicates...")
        for group in groups:
            subgroup = []

            for entry in group:
                correspondingDataPoint = [d for d in data if d.get("oqmdId") == entry.label]

                sg = gemmi.find_spacegroup_by_name(correspondingDataPoint[0].get("symmetry"))
                correspondingDataPoint[0]["symmetry"] = sg.number

                subgroup.append(correspondingDataPoint)
            
            log_debug(str(subgroup))

            sortedSubgroup = sorted(subgroup, key=lambda x: (x[0]['bandGap'], -x[0]['symmetry']))
            sortedGroups.append(sortedSubgroup)

            finalizedCandidates = []

            log_debug("Finalizing candidates...")
            for group in sortedGroups:
                finalizedCandidates.append(group[0])

            finalizedSorted = sorted(finalizedCandidates, key=lambda x: (x[0]['bandGap'], -x[0]['symmetry']))
        
        return finalizedSorted
    else:
        return data[0]