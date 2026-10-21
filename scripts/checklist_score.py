"""Manipulation check: score descriptions with a 15-question yes/no checklist.

Items: 16 real tools x 3 variants (48) + 30 fake-tool descriptions (seed 2026, 10 fakes x 3 variants).
Two judge models, temperature 0. Score = fraction of 'yes'. Answer 'no' when a question does not apply.

Usage:
  python scripts/checklist_score.py score --judges <model_a> <model_b>     -> checklist/judge_scores.csv
  python scripts/checklist_score.py human-sheet                             -> checklist/human_sheet.csv (blind)
  python scripts/checklist_score.py report                                  -> prints pass/fail
"""
import argparse
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QS = json.loads((ROOT / "checklist" / "questions.json").read_text())
VARIANTS = ("dmin", "dorig", "drich")

JUDGE_PROMPT = """You are checking the documentation of one API tool for an AI agent.

Tool:
{tool}

Answer each question with true or false. Answer false if the question does not apply.
Questions:
{questions}

Output ONLY a JSON list of {n} booleans, in question order."""


def items():
    from harness.variants import make_doc  # noqa: F401  (format check only)
    out = []
    for v in VARIANTS:
        d = json.loads((ROOT / "descriptions" / f"{v}.json").read_text())
        out += [{"item": f"real:{n}:{v}", "tool": n, "variant": v, "name": n, "entry": e} for n, e in d.items()]
    fakes = []
    for kind in ("lookalike", "indomain", "unrelated"):
        fakes += json.loads((ROOT / "fake_tools" / f"{kind}.json").read_text())
    fakes.sort(key=lambda s: s["name"])
    for s in random.Random(2026).sample(fakes, 10):
        out += [{"item": f"fake:{s['name']}:{v}", "tool": s["name"], "variant": v, "name": s["name"],
                 "entry": s["desc"][v]} for v in VARIANTS]
    return out


def render(it):
    return json.dumps({"name": it["name"], "description": it["entry"]["desc"],
                       "parameter_descriptions": it["entry"].get("params") or {}}, indent=2)


def ask(model, it):
    import litellm
    p = JUDGE_PROMPT.format(tool=render(it), n=len(QS),
                            questions="\n".join(f"{i+1}. {q['q']}" for i, q in enumerate(QS)))
    r = litellm.completion(model=model, temperature=0, messages=[{"role": "user", "content": p}])
    text = r.choices[0].message.content.strip()
    if text.startswith("```"):  # tolerate a code fence around the JSON list
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    ans = json.loads(text)
    assert len(ans) == len(QS) and all(isinstance(x, bool) for x in ans), f"{model} on {it['item']}: {text[:200]}"
    return ans


def score(judges):
    with open(ROOT / "checklist" / "judge_scores.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "tool", "variant", "judge"] + [q["id"] for q in QS])
        for it in items():
            for j in judges:
                w.writerow([it["item"], it["tool"], it["variant"], j] + [int(x) for x in ask(j, it)])


def human_sheet():
    its = [i for i in items() if i["item"].startswith("real:")]
    tools = sorted({i["tool"] for i in its})
    chosen = set(random.Random(2026).sample(tools, 10))
    sel = [i for i in its if i["tool"] in chosen]
    random.Random(7).shuffle(sel)
    key = {f"H{k:02d}": i["item"] for k, i in enumerate(sel)}
    (ROOT / "checklist" / "human_key.json").write_text(json.dumps(key, indent=2))  # do not open until done
    with open(ROOT / "checklist" / "human_sheet.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["blind_id", "tool_text"] + [q["id"] for q in QS])
        for bid, i in zip(key, sel):
            w.writerow([bid, render(i)] + [""] * len(QS))


def report():
    import krippendorff
    import numpy as np
    from scipy.stats import wilcoxon
    rows = list(csv.DictReader(open(ROOT / "checklist" / "judge_scores.csv")))
    qids = [q["id"] for q in QS]
    judges = sorted({r["judge"] for r in rows})
    by = {(r["item"], r["judge"]): [int(r[q]) for q in qids] for r in rows}
    item_ids = sorted({r["item"] for r in rows})
    data = np.array([[v for it in item_ids for v in by[(it, j)]] for j in judges])
    alpha = krippendorff.alpha(reliability_data=data, level_of_measurement="nominal")
    mean = {it: np.mean([np.mean(by[(it, j)]) for j in judges]) for it in item_ids}
    real = sorted({it.split(":")[1] for it in item_ids if it.startswith("real:")})
    s = {v: np.array([mean[f"real:{t}:{v}"] for t in real]) for v in VARIANTS}
    p1 = wilcoxon(s["dorig"], s["dmin"], alternative="greater").pvalue
    p2 = wilcoxon(s["drich"], s["dorig"], alternative="greater").pvalue
    print(f"judges={judges} alpha={alpha:.3f} (need >= 0.6)")
    print({v: round(float(s[v].mean()), 3) for v in VARIANTS})
    print(f"dorig > dmin p={p1:.4g}; drich > dorig p={p2:.4g} (need < 0.05 each)")
    print("PASS" if alpha >= 0.6 and p1 < 0.05 and p2 < 0.05 else "FAIL")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("score").add_argument("--judges", nargs=2, required=True)
    sub.add_parser("human-sheet")
    sub.add_parser("report")
    a = ap.parse_args()
    {"score": lambda: score(a.judges), "human-sheet": human_sheet, "report": report}[a.cmd]()


if __name__ == "__main__":
    main()
