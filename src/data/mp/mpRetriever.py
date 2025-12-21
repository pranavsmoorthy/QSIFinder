import os
from mp_api.client import MPRester
from dotenv import load_dotenv

load_dotenv()
MP_KEY = os.getenv("MP_KEY")

with MPRester(MP_KEY) as mpr:
    docs = mpr.materials.summary.search(
        material_ids=["mp-149"],
        fields=["material_id", "band_gap", "volume"]
    )

    print(docs)