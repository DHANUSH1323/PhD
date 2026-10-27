"""Exit 1 if a cell's saved results show mass infrastructure failures (credits gone, provider down).
Usage: python scripts/check_cell_health.py results/raw/main__exp_C3__<agent>/results.json [max_failures]
"""
import json
import sys

path = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
try:
    sims = json.load(open(path))["simulations"]
except FileNotFoundError:
    print(f"health: no results file yet at {path}")
    sys.exit(0)
bad = [s for s in sims if s.get("termination_reason") == "infrastructure_error"]
print(f"health: {len(sims)} conversations saved, {len(bad)} infrastructure errors (limit {limit})")
if len(bad) > limit:
    print("health: STOP, see the cell log for the provider error")
    sys.exit(1)
