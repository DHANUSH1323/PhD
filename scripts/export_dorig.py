"""Write descriptions/dorig.json from the retail docstrings, and dmin.json by rule.

D-min rule: the first sentence of the D-orig description; no parameter descriptions.
"""
import json
import re
from pathlib import Path

from docstring_parser import parse
from tau2.domains.retail.data_model import RetailDB
from tau2.domains.retail.tools import RetailTools
from tau2.domains.retail.utils import RETAIL_DB_PATH

OUT = Path(__file__).resolve().parent.parent / "descriptions"

kit = RetailTools(RetailDB.load(RETAIL_DB_PATH))
dorig, dmin = {}, {}
for name in sorted(kit._func_tools):
    doc = parse(getattr(kit, name).__doc__ or "")
    desc = doc.short_description or ""
    if doc.long_description:
        desc += "\n\n" + doc.long_description
    dorig[name] = {"desc": desc, "params": {p.arg_name: p.description for p in doc.params}}
    first = re.split(r"(?<=[.!?])\s", " ".join(desc.split()), maxsplit=1)[0]
    dmin[name] = {"desc": first, "params": {}}
OUT.mkdir(exist_ok=True)
(OUT / "dorig.json").write_text(json.dumps(dorig, indent=2))
(OUT / "dmin.json").write_text(json.dumps(dmin, indent=2))
print(f"wrote {len(dorig)} tools")
