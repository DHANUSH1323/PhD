"""Acceptance check for fake_tools/{lookalike,indomain,unrelated}.json. Offline, no API.

Usage: python scripts/check_fakes.py [--need-drich]
Prints one line per check and ends with ALL PASS or a list of failures.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from tau2.domains.retail.environment import get_environment

ROOT = Path(__file__).resolve().parent.parent
TYPES = {"str", "int", "float", "bool", "list[str]", "dict"}
# Words that would make an in-domain tool claim a real retail tool's job (rule F-I3).
REAL_JOBS = ("cancel", "return", "exchange", "refund", "modify", "change the address", "shipping address",
             "default address", "order status", "order details", "user details", "find user", "human agent",
             "transfer", "payment method", "track")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--need-drich", action="store_true")
    a = ap.parse_args()
    real = {t.name: t for t in get_environment().get_tools()}
    real_sets = {n: set(t.openai_schema["function"]["parameters"].get("properties", {})) for n, t in real.items()}
    real_params = {n: [(p, s.get("type")) for p, s in t.openai_schema["function"]["parameters"].get("properties", {}).items()]
                   for n, t in real.items()}
    fails = []

    def check(ok, msg):
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    files = {k: json.loads((ROOT / "fake_tools" / f"{k}.json").read_text())
             for k in ("lookalike", "indomain", "unrelated") if (ROOT / "fake_tools" / f"{k}.json").exists()}
    variants = ("dmin", "dorig", "drich") if a.need_drich else ("dmin", "dorig")
    all_names = Counter(s["name"] for specs in files.values() for s in specs)
    check(all(c == 1 for c in all_names.values()), "names unique across all fake files")
    for kind, specs in files.items():
        names = [s["name"] for s in specs]
        check(not set(names) & set(real), f"{kind}: no name equals a real tool")
        check(all(s.get("kind") == kind for s in specs), f"{kind}: every entry has kind={kind}")
        check(all(p["type"] in TYPES for s in specs for p in s["params"]), f"{kind}: parameter types allowed")
        check(all(v in s["desc"] for s in specs for v in variants), f"{kind}: every entry has {', '.join(variants)}")
        check(all(s["desc"]["dmin"]["params"] == {} for s in specs), f"{kind}: dmin has no parameter text")
        check(all("use " not in s["error"].lower() and not any(r in s["error"] for r in real) for s in specs),
              f"{kind}: no error names or points to a tool")
    if "lookalike" in files:
        L = files["lookalike"]
        check(len(L) == 64, f"lookalike: 64 entries (found {len(L)})")
        check(all("rank" in s for s in L), "lookalike: every entry has rank")
        check(Counter(s.get("rank") for s in L) == {1: 16, 2: 16, 3: 16, 4: 16}, "lookalike: ranks 1 to 4, 16 each")
        check(all(Counter(s["sibling"] for s in L if s.get("rank") == r) == Counter({n: 1 for n in real})
                  for r in (1, 2, 3, 4)), "lookalike: each real tool has exactly one look-alike per rank")
        check(all({p["name"] for p in s["params"]} == real_sets.get(s["sibling"]) for s in L),
              "lookalike: parameter names equal the sibling's")
        check(all(s["subtype"] in ("near_duplicate", "schema_compatible") for s in L), "lookalike: subtype allowed")
    if "indomain" in files:
        I = files["indomain"]
        check(len(I) == 48, f"indomain: 48 entries (found {len(I)})")
        check(all("rank" not in s and s.get("sibling") is None for s in I), "indomain: no rank, sibling null")
        check(all(s["subtype"] == "in_domain_other_function" for s in I), "indomain: subtype")
        check(all(s["error"] == "This service is currently unavailable." for s in I), "indomain: error text")
        check(not [s["name"] for s in I if {p["name"] for p in s["params"]} in real_sets.values()],
              "indomain: no parameter set equals a real tool's")
        bad = [s["name"] for s in I if any(w in s["desc"]["dorig"]["desc"].lower() for w in REAL_JOBS)]
        check(not bad, f"indomain: no dorig claims a real tool's job {bad if bad else ''}")
    if "unrelated" in files:
        U = files["unrelated"]
        check(len(U) == 48, f"unrelated: 48 entries (found {len(U)})")
        check(all(s.get("sibling") is None and s["subtype"] == "cross_domain" for s in U), "unrelated: subtype, sibling null")
        check(all(s.get("source", "").split(":")[0] in ("tau2", "bfcl") for s in U), "unrelated: source is tau2 or bfcl")
    print("ALL PASS" if not fails else f"{len(fails)} FAILED")
    raise SystemExit(1 if fails else 0)


if __name__ == "__main__":
    main()
