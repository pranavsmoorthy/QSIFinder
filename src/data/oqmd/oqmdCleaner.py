from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from utils.debug import log_debug

def filter(data):
    if data[0].get("dataFound"):
        log_debug("Filtering...")

        ids = []
        matcher = StructureMatcher()
        opt = OptimadeRester("oqmd")

        for d in data:
            ids.append(d.get("oqmdId"))

        filterStr = " OR ".join([f'_oqmd_entry_id={i}' for i in ids])

        opt = OptimadeRester("oqmd")
        results = opt.get_structures('chemical_formula_reduced="Fe2O3"')

        log_debug(str(results))

        structures = list(results['oqmd'].values())

        return structures
    else:
        return data[0]