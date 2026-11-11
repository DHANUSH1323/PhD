"""Amendment 2 analysis (RESEARCH_PLAN.md, Amendment 2): dorig cells C12 to C15.

Contrasts F1 to F5, paired bootstrap over tasks (10,000 resamples, seed 300), Holm within the
family, plus the "#"-less order_id count per new cell. Writes results/amendment2_results.md and
results/amendment2_contrasts.csv.
"""
import csv
import glob
import json
from pathlib import Path

import numpy as np

from analysis.primary import boot, holm, B, SEED  # noqa: F401  (same bootstrap as block 1)

ROOT = Path(__file__).resolve().parent.parent
CELLS = ["C1", "C2", "C12", "C13", "C14", "C15", "C5", "C6", "C3", "C4", "C9"]
LABEL = {"C1": "16 real, short (no parameter text)", "C2": "16 real, rich",
         "C12": "16 real, benchmark's own (dorig)", "C13": "+48 look-alike, dorig",
         "C14": "+40 look-alike, dorig, token-matched to C2 (8,227 vs 8,232)",
         "C15": "+48 cross-domain, dorig", "C5": "+48 look-alike, short", "C6": "+48 look-alike, rich",
         "C3": "+48 cross-domain, short", "C4": "+48 cross-domain, rich",
         "C9": "+54 look-alike, short (5,043 tokens, not matched)"}
F = [("F1", "P(C12) - P(C1)", "C12", "C1", "cost of deleting the benchmark's parameter text"),
     ("F2", "P(C2) - P(C12)", "C2", "C12", "gain of enrichment over the benchmark's own text"),
     ("F3", "P(C13) - P(C12)", "C13", "C12", "look-alike damage under the benchmark's own text"),
     ("F4", "P(C2) - P(C14)", "C2", "C14", "equal provider tokens: 16 rich vs 16 + 40 look-alike dorig"),
     ("F5", "P(C15) - P(C12)", "C15", "C12", "cross-domain damage under the benchmark's own text")]


def load():
    R = {}
    for c in CELLS:
        paths = glob.glob(str(ROOT / f"results/raw/main__exp_{c}__*/results.json"))
        if not paths:
            continue
        sims = json.load(open(paths[0]))["simulations"]
        R[c] = {s["task_id"]: float(s["reward_info"]["reward"]) for s in sims}
    tasks = sorted(R["C1"])
    for c in list(R):
        if set(R[c]) != set(tasks):  # a cell still running is left out, not partially used
            print(f"skipping {c}: {len(R[c])} of {len(tasks)} tasks")
            del R[c]
    return tasks, {c: np.array([R[c][t] for t in tasks]) for c in R}


def no_hash(c):
    path = glob.glob(str(ROOT / f"results/raw/main__exp_{c}__*/results.json"))[0]
    sims = json.load(open(path))["simulations"]
    f = fnh = 0
    for s in sims:
        ok = s["reward_info"]["reward"] == 1
        nh = any(isinstance((tc.get("arguments") or {}).get("order_id"), str)
                 and not (tc["arguments"]["order_id"] or "#").strip().startswith("#")
                 for m in s["messages"] for tc in (m.get("tool_calls") or []))
        f += not ok; fnh += (not ok) and nh
    return f, fnh


def main():
    tasks, P = load()
    rng = np.random.default_rng(SEED)
    out = ["# Amendment 2 results: the benchmark's own descriptions (114 tasks, 1 trial per cell)\n",
           "Follow-up cells run 2026-11-10 after block-1 results were viewed (RESEARCH_PLAN.md, Amendment 2).\n",
           "## pass^1 per cell\n\n| cell | setup | pass^1 | passed/114 |\n|---|---|---|---|"]
    for c in CELLS:
        if c in P:
            out.append(f"| {c} | {LABEL[c]} | {P[c].mean():.3f} | {int(P[c].sum())} |")
    rows = []
    for key, name, a, b, meaning in F:
        if a in P and b in P:
            est, lo, hi, p = boot(P[a] - P[b], rng)
            rows.append({"contrast": key, "definition": name, "estimate": est, "ci_low": lo, "ci_high": hi, "p": p,
                         "meaning": meaning})
    ph = holm([r["p"] for r in rows])
    for r, q in zip(rows, ph):
        r["p_holm"] = q
    out.append("\n## Contrasts (paired bootstrap over tasks, 10,000 resamples, two-sided p, Holm over F1 to F5)\n")
    out.append("| contrast | definition | estimate | 95% CI | p | p (Holm) | what it measures |\n|---|---|---|---|---|---|---|")
    for r in rows:
        out.append(f"| {r['contrast']} | {r['definition']} | {r['estimate']:+.3f} | [{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] "
                   f"| {r['p']:.3f} | {r['p_holm']:.3f} | {r['meaning']} |")
    out.append("\n## Order ids passed without '#', failed conversations\n\n| cell | failed | failed with a '#'-less order_id |\n|---|---|---|")
    for c in ["C1", "C12", "C2", "C13", "C14", "C15"]:
        if c in P:
            f, fnh = no_hash(c)
            out.append(f"| {c} | {f} | {fnh} |")
    with open(ROOT / "results/amendment2_contrasts.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (ROOT / "results/amendment2_results.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
