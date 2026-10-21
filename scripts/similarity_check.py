"""Similarity check for the three fake-tool kinds, and selection of the cross-domain set.

Each fake's score = max cosine similarity of its dorig text to any of the 16 real tools.
Required ordering: look-alike (ranks 1 to 3) > in-domain > cross-domain,
each step tested with a one-sided Mann-Whitney U test at p < 0.05.

Usage:
  python scripts/similarity_check.py --embed <S> --select-unrelated 48
      draws 48 cross-domain tools (seed 2026) from fake_tools/unrelated_candidates.json,
      eligible only if their score is below the lowest look-alike score AND below the in-domain median,
      writes fake_tools/unrelated.json,
      then runs the check
  python scripts/similarity_check.py --embed <S>
      runs the check on the existing files (run it once more with --embed <R> as a robustness check;
      that run selects nothing and writes results/similarity_<tag>.csv when --tag is given)
"""
import argparse
import csv
import json
import random
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

from harness.embed import get_embedder

ROOT = Path(__file__).resolve().parent.parent
FT = ROOT / "fake_tools"

# Cross-domain candidates whose name or description carries any of these words are never
# selected. The embedding cut alone keeps shopping-flavoured tools (checked Oct 20: two of
# four stayed eligible under the in-domain median), so the far rung is cleaned by keyword.
SHOP_WORDS = ("grocery", "vegan", "product", "cart", "bill", "purchase", "customer", "order",
              "shop", "store", "retail", "coupon", "delivery", "shipping", "refund", "invoice")


def shop_flavoured(spec) -> bool:
    blob = (spec["name"] + " " + spec["desc"]["dorig"]["desc"]).lower().replace("_", " ")
    return any(w in blob for w in SHOP_WORDS)


def text(name, entry, param_names):
    return f"{name} {entry['desc']} {' '.join(param_names)}"


def scores(specs, real_mat, embed):
    m = np.asarray(embed([text(s["name"], s["desc"]["dorig"], [p["name"] for p in s["params"]]) for s in specs]))
    m = m / np.linalg.norm(m, axis=1, keepdims=True)
    return (m @ real_mat.T).max(axis=1).tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed", required=True)
    ap.add_argument("--select-unrelated", type=int, default=None)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    embed = get_embedder(a.embed)
    real = json.loads((ROOT / "descriptions" / "dorig.json").read_text())
    real_mat = np.asarray(embed([text(n, e, list(e["params"])) for n, e in real.items()]))
    real_mat = real_mat / np.linalg.norm(real_mat, axis=1, keepdims=True)

    look = [s for s in json.loads((FT / "lookalike.json").read_text()) if s.get("rank", 1) <= 3]
    ind = json.loads((FT / "indomain.json").read_text())
    ls, ins = scores(look, real_mat, embed), scores(ind, real_mat, embed)

    if a.select_unrelated:
        cand = json.loads((FT / "unrelated_candidates.json").read_text())
        cs = scores(cand, real_mat, embed)
        cut = min(min(ls), float(np.median(ins)))
        below = [s for s, v in zip(cand, cs) if v < cut]
        eligible = sorted([s for s in below if not shop_flavoured(s)], key=lambda s: s["name"])
        print(f"cross-domain candidates {len(cand)}, cut {cut:.3f} (lowest look-alike {min(ls):.3f}, "
              f"in-domain median {np.median(ins):.3f}), below cut {len(below)}, "
              f"eligible after keyword filter {len(eligible)}")
        if len(eligible) < a.select_unrelated:
            raise SystemExit("Not enough eligible cross-domain tools: add more BFCL candidates.")
        chosen = random.Random(2026).sample(eligible, a.select_unrelated)
        (FT / "unrelated.json").write_text(json.dumps(chosen, indent=2))
        print(f"wrote {len(chosen)} cross-domain tools")

    unr = json.loads((FT / "unrelated.json").read_text())
    us = scores(unr, real_mat, embed)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    suffix = f"_{a.tag}" if a.tag else ""
    with open(out / f"similarity{suffix}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "kind", "max_sim_to_real", "embed_model"])
        for kind, specs, vals in (("lookalike", look, ls), ("indomain", ind, ins), ("unrelated", unr, us)):
            w.writerows([(s["name"], kind, v, a.embed) for s, v in zip(specs, vals)])
    for kind, vals in (("look-alike", ls), ("in-domain", ins), ("cross-domain", us)):
        print(f"{kind:13s} n={len(vals)} mean={np.mean(vals):.3f} median={np.median(vals):.3f}")
    p1 = mannwhitneyu(ls, ins, alternative="greater").pvalue
    p2 = mannwhitneyu(ins, us, alternative="greater").pvalue
    print(f"look-alike > in-domain: p={p1:.3g}; in-domain > cross-domain: p={p2:.3g}")
    print(f"overlap: in-domain at or above lowest look-alike {sum(v >= min(ls) for v in ins)}; "
          f"cross-domain at or above lowest in-domain {sum(v >= min(ins) for v in us)}")
    print("PASS" if p1 < 0.05 and p2 < 0.05 else "FAIL")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        for label, vals in (("look-alike", ls), ("in-domain", ins), ("cross-domain", us)):
            plt.hist(vals, bins=20, alpha=0.5, label=f"{label} ({len(vals)})")
        plt.xlabel("max cosine similarity to a real retail tool")
        plt.ylabel("tools")
        plt.legend()
        plt.savefig(out / f"similarity{suffix}.png", dpi=150)
    except ImportError:
        pass


if __name__ == "__main__":
    main()
