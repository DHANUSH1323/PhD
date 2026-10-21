"""Prepare descriptions/drich_check.md for the hand-check of the rich descriptions.

For each real tool, one row per sentence of the drich description. Each row shows the
sentence, any policy.md line it closely echoes (a warning: drich must not add policy that
dorig lacks), whether the sentence already appears in dorig, and candidate lines in
tools.py found by keyword, so the reviewer can write the enforcing line or NOT ENFORCED.

The script only prepares the table. The judgement is the reviewer's.

Usage: PYTHONPATH=. python scripts/drich_check.py [--variant drich]
"""
import argparse
import json
import re
from pathlib import Path

from tau2.domains.retail.utils import RETAIL_POLICY_PATH

ROOT = Path(__file__).resolve().parent.parent
TOOLS_PY = ROOT / "benchmarks" / "tau2-bench" / "src" / "tau2" / "domains" / "retail" / "tools.py"
STOP = set("the a an of to in for and or is are be it this that with by on as from at its their which "
           "such only can will not no if when use used using each any all should must may does do".split())


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", " ".join(text.split())) if s.strip()]


def keywords(sentence: str) -> set[str]:
    return {w for w in re.findall(r"[a-z_]{4,}", sentence.lower()) if w not in STOP}


def method_lines(src: str, name: str) -> list[tuple[int, str]]:
    lines = src.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(rf"\s+def {name}\(", l)), None)
    if start is None:
        return []
    out = []
    for i in range(start + 1, len(lines)):
        if re.match(r"\s{4}def ", lines[i]) or re.match(r"\s{4}@", lines[i]):
            break
        out.append((i + 1, lines[i]))
    return out


def overlap(a: set[str], b: set[str]) -> float:
    return len(a & b) / max(1, len(a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="drich")
    a = ap.parse_args()
    rich = json.loads((ROOT / "descriptions" / f"{a.variant}.json").read_text())
    dorig = json.loads((ROOT / "descriptions" / "dorig.json").read_text())
    policy = [s for s in sentences(RETAIL_POLICY_PATH.read_text()) if len(s) > 30]
    src = TOOLS_PY.read_text()
    out = [f"# Hand-check of {a.variant} against tools.py and policy.md\n",
           "One row per sentence. Fill the last column with the enforcing line in tools.py "
           "(for example `tools.py:214`) or `NOT ENFORCED`. Delete from the json any sentence marked "
           "NOT ENFORCED that states a constraint, and any sentence flagged POLICY that is absent from dorig.\n"]
    for name in sorted(rich):
        out.append(f"\n## {name}\n")
        out.append("| # | sentence | in dorig | policy echo | candidate tools.py lines | enforced by |")
        out.append("|---|---|---|---|---|---|")
        dorig_text = " ".join(dorig[name]["desc"].split()).lower()
        body = method_lines(src, name)
        for i, s in enumerate(sentences(rich[name]["desc"]), 1):
            kw = keywords(s)
            in_dorig = "yes" if s.lower() in dorig_text else ""
            pol = max(policy, key=lambda p: overlap(kw, keywords(p)), default="")
            pol_flag = "POLICY: " + pol[:80] if pol and overlap(kw, keywords(pol)) >= 0.5 and not in_dorig else ""
            cands = [f"{n}: `{l.strip()[:60]}`" for n, l in body
                     if kw & keywords(l) and ("raise" in l or "if " in l or "return" in l)][:3]
            out.append(f"| {i} | {s} | {in_dorig} | {pol_flag} | {'<br>'.join(cands)} | |")
    path = ROOT / "descriptions" / f"{a.variant}_check.md"
    path.write_text("\n".join(out) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
