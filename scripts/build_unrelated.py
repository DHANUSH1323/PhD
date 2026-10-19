"""Build the candidate pool for unrelated fakes (before the similarity filter).

Sources: tau2 airline and telecom tools (names that collide with retail removed)
and BFCL v4 `multiple` functions. Writes fake_tools/unrelated_candidates.json with
dorig and dmin filled; drich is added later by scripts/generate_drich.py.

Usage: python scripts/build_unrelated.py --bfcl <path to BFCL_v4_multiple.json>
"""
import argparse
import json
import re
from pathlib import Path

from tau2.registry import registry

ROOT = Path(__file__).resolve().parent.parent
JSON_TYPES = {"string": "str", "integer": "int", "number": "float", "float": "float",
              "boolean": "bool", "array": "list[str]", "object": "dict", "dict": "dict"}
ERROR = "The request could not be completed."


def first_sentence(text: str) -> str:
    return re.split(r"(?<=[.!?])\s", " ".join(text.split()), maxsplit=1)[0]


def to_spec(name, description, properties, required, source):
    params, pdesc = [], {}
    for p, sch in properties.items():
        t = JSON_TYPES.get(sch.get("type"))
        if t is None:
            return None  # unsupported parameter type: skip this function
        params.append({"name": p, "type": t, "required": p in required})
        if sch.get("description"):
            pdesc[p] = sch["description"]
    return {"name": name, "kind": "unrelated", "sibling": None, "subtype": "cross_domain",
            "source": source, "params": params, "error": ERROR,
            "desc": {"dorig": {"desc": description, "params": pdesc},
                     "dmin": {"desc": first_sentence(description), "params": {}}}}


def tau2_tools(domain, banned):
    out = []
    for t in registry.get_env_constructor(domain)().get_tools():
        f = t.openai_schema["function"]
        if f["name"] in banned:
            continue
        s = to_spec(f["name"], f["description"], f["parameters"].get("properties", {}),
                    set(f["parameters"].get("required", [])), f"tau2:{domain}")
        if s:
            out.append(s)
    return out


def bfcl_tools(path, banned):
    out, seen = [], set(banned)
    for line in open(path):
        for fn in json.loads(line).get("function", []):
            name = re.sub(r"[^a-zA-Z0-9_-]", "_", fn["name"])
            if name in seen:
                continue
            p = fn.get("parameters", {})
            s = to_spec(name, fn.get("description", ""), p.get("properties", {}),
                        set(p.get("required", [])), "bfcl:multiple")
            if s and s["desc"]["dorig"]["desc"]:
                out.append(s)
                seen.add(name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bfcl", required=False)
    a = ap.parse_args()
    retail = {t.name for t in registry.get_env_constructor("retail")().get_tools()}
    pool = tau2_tools("airline", retail) + tau2_tools("telecom", retail)
    if a.bfcl:
        pool += bfcl_tools(a.bfcl, retail | {s["name"] for s in pool})
    path = ROOT / "fake_tools" / "unrelated_candidates.json"
    path.write_text(json.dumps(pool, indent=2))
    print(f"{len(pool)} candidates -> {path}")


if __name__ == "__main__":
    main()
