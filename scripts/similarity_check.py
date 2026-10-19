"""Similarity check and selection of the 48 unrelated fakes.

For every fake: max cosine similarity (dorig text) to any of the 16 real tools.
Look-alikes must all score above every selected unrelated tool.

Usage: python scripts/similarity_check.py --embed <spec> [--select 48]
  --select N  writes fake_tools/unrelated.json with N unrelated tools drawn (seed 2026)
              from candidates scoring below the lowest look-alike.
"""
import argparse
import csv
import json
import random
from pathlib import Path

import numpy as np

from harness.embed import get_embedder

ROOT = Path(__file__).resolve().parent.parent


def text(name, entry, param_names):
    return f"{name} {entry['desc']} {' '.join(param_names)}"


def max_sims(specs, real_mat, embed):
    if not specs:
        return []
    m = np.asarray(embed([text(s["name"], s["desc"]["dorig"], [p["name"] for p in s["params"]]) for s in specs]))
    m = m / np.linalg.norm(m, axis=1, keepdims=True)
    return (m @ real_mat.T).max(axis=1).tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed", required=True)
    ap.add_argument("--select", type=int, default=None)
    a = ap.parse_args()
    embed = get_embedder(a.embed)
    real = json.loads((ROOT / "descriptions" / "dorig.json").read_text())
    real_mat = np.asarray(embed([text(n, e, list(e["params"])) for n, e in real.items()]))
    real_mat = real_mat / np.linalg.norm(real_mat, axis=1, keepdims=True)
    look = json.loads((ROOT / "fake_tools" / "lookalike.json").read_text())
    cand = json.loads((ROOT / "fake_tools" / "unrelated_candidates.json").read_text())
    ls, us = max_sims(look, real_mat, embed), max_sims(cand, real_mat, embed)
    floor = min(ls)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with open(out / "similarity.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "kind", "max_sim_to_real", "embed_model"])
        w.writerows([(s["name"], "lookalike", v, a.embed) for s, v in zip(look, ls)])
        w.writerows([(s["name"], "unrelated_candidate", v, a.embed) for s, v in zip(cand, us)])
    eligible = [s for s, v in zip(cand, us) if v < floor]
    print(f"look-alike min {floor:.3f}; candidates {len(cand)}, eligible below floor {len(eligible)}")
    if a.select:
        if len(eligible) < a.select:
            raise SystemExit(f"Only {len(eligible)} eligible; add BFCL candidates.")
        eligible.sort(key=lambda s: s["name"])
        chosen = random.Random(2026).sample(eligible, a.select)
        (ROOT / "fake_tools" / "unrelated.json").write_text(json.dumps(chosen, indent=2))
        print(f"wrote {len(chosen)} unrelated tools")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        sel = {s["name"] for s in json.loads((ROOT / "fake_tools" / "unrelated.json").read_text())} \
            if (ROOT / "fake_tools" / "unrelated.json").exists() else set()
        sel_vals = [v for s, v in zip(cand, us) if s["name"] in sel]
        plt.hist(ls, bins=20, alpha=0.6, label="look-alike")
        plt.hist(sel_vals or us, bins=20, alpha=0.6, label="unrelated (selected)" if sel_vals else "unrelated (candidates)")
        plt.xlabel("max cosine similarity to a real retail tool")
        plt.ylabel("tools")
        plt.legend()
        plt.savefig(out / "similarity.png", dpi=150)
    except ImportError:
        pass


if __name__ == "__main__":
    main()
