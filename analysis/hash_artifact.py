"""Count conversations where the agent passed an order_id without the leading '#' (Amendment 2).

D-min removed every parameter description, including the benchmark's warning that order ids
start with '#'. This counts, per cell, how many conversations contain at least one such call,
split by pass/fail, from results/raw/main__exp_C*/results.json.

Usage: python analysis/hash_artifact.py  -> prints a table and writes results/hash_artifact.csv
"""
import csv
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "hash_artifact.csv"


def no_hash_calls(sim) -> int:
    n = 0
    for m in sim.get("messages", []):
        for tc in (m.get("tool_calls") or []):
            args = tc.get("arguments") or {}
            oid = args.get("order_id")
            if isinstance(oid, str) and oid.strip() and not oid.strip().startswith("#"):
                n += 1
    return n


def main():
    rows = []
    for path in sorted(glob.glob(str(ROOT / "results/raw/main__exp_C*__*/results.json"))):
        cell = re.search(r"main__exp_(C\d+)__", path).group(1)
        sims = json.load(open(path))["simulations"]
        passed = failed = passed_nh = failed_nh = 0
        for s in sims:
            ok = (s.get("reward_info") or {}).get("reward", 0) == 1
            nh = no_hash_calls(s) > 0
            passed += ok; failed += not ok
            passed_nh += ok and nh; failed_nh += (not ok) and nh
        rows.append({"cell": cell, "n": len(sims), "failed": failed, "failed_with_no_hash_id": failed_nh,
                     "passed": passed, "passed_with_no_hash_id": passed_nh})
    rows.sort(key=lambda r: int(r["cell"][1:]))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{'cell':5} {'n':>4} {'failed':>7} {'no#fail':>8} {'passed':>7} {'no#pass':>8}")
    for r in rows:
        print(f"{r['cell']:5} {r['n']:>4} {r['failed']:>7} {r['failed_with_no_hash_id']:>8} {r['passed']:>7} {r['passed_with_no_hash_id']:>8}")


if __name__ == "__main__":
    main()
