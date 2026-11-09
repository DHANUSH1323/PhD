"""Retriever recall in cells C7 and C8: for every agent turn, replay the top-16 selection
exactly as harness/agents.py does (user messages so far, last 2,000 characters, cosine
similarity under the retriever model) and ask whether the tools the task needs were shown.

Writes results/retriever_recall.csv (one row per conversation and turn) and prints a summary.
"""
import csv
import glob
import json
from pathlib import Path

import numpy as np

from types import SimpleNamespace

from harness.agents import order_tools, tool_text
from harness.cells import get_cell
from harness.embed import get_embedder
from harness.toolkit import make_env_constructor

ROOT = Path(__file__).resolve().parent.parent
K, QUERY_CHARS = 16, 2000
RETRIEVER = "st:sentence-transformers/all-MiniLM-L6-v2"


def main():
    emb = get_embedder(RETRIEVER)
    rows = []
    for c in ("C7", "C8"):
        env = make_env_constructor(get_cell(c))()
        tools = env.get_tools()
        names = [t.name for t in tools]
        real = set(json.load(open(ROOT / "descriptions/dorig.json")))
        mat = np.asarray(emb([tool_text(t) for t in tools]), dtype=float)
        mat /= np.linalg.norm(mat, axis=1, keepdims=True)
        d = json.load(open(glob.glob(str(ROOT / f"results/raw/main__exp_{c}__*/results.json"))[0]))
        tasks = {t["id"]: t for t in d["tasks"]}
        for s in d["simulations"]:
            gold = sorted({a["name"] for a in (tasks[s["task_id"]].get("evaluation_criteria") or {}).get("actions", [])})
            if not gold:
                continue
            users, turn = [], 0
            first16 = {t.name for t in order_tools(tools, SimpleNamespace(id=s["task_id"]))[:K]}  # what the harness shows before any user message
            for m in s["messages"]:
                if m.get("role") == "user" and m.get("content"):
                    users.append(m["content"])
                if m.get("role") == "assistant":
                    turn += 1
                    text = " ".join(users)[-QUERY_CHARS:]
                    if text.strip():
                        q = np.asarray(emb([text])[0], dtype=float)
                        q /= np.linalg.norm(q)
                        top = np.argsort(-(mat @ q), kind="stable")[:K]
                        shown = {names[i] for i in top}
                    else:
                        shown = first16
                    hit = sum(1 for g in gold if g in shown)
                    rows.append(dict(cell=c, task_id=s["task_id"], turn=turn, n_gold=len(gold), gold_shown=hit,
                                     recall=hit / len(gold), real_shown=sum(1 for n in shown if n in real),
                                     reward=float(s["reward_info"]["reward"])))
    with open(ROOT / "results/retriever_recall.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for c in ("C7", "C8"):
        rs = [r for r in rows if r["cell"] == c]
        by_task = {}
        for r in rs:
            by_task.setdefault(r["task_id"], []).append(r)
        mean_recall = np.mean([r["recall"] for r in rs])
        ever_all = np.mean([max(r["gold_shown"] for r in v) == v[0]["n_gold"] for v in by_task.values()])
        ever_any = np.mean([any(r["gold_shown"] == r["n_gold"] for r in v) for v in by_task.values()])
        real = np.mean([r["real_shown"] for r in rs])
        first_turn_full = [next((r["turn"] for r in v if r["gold_shown"] == r["n_gold"]), None) for v in by_task.values()]
        print(f"{c}: {len(by_task)} conversations, {len(rs)} agent turns | mean recall of needed tools per turn {mean_recall:.2f} | "
              f"real tools among the 16 shown, mean {real:.1f} | conversations where ALL needed tools were shown at once in some turn {ever_any:.0%} | "
              f"pass rate when that happened {np.mean([v[0]['reward'] for v in by_task.values() if any(r['gold_shown']==r['n_gold'] for r in v)]) if any(first_turn_full) else float('nan'):.2f} "
              f"vs {np.mean([v[0]['reward'] for v in by_task.values() if not any(r['gold_shown']==r['n_gold'] for r in v)]):.2f} when it never did")


if __name__ == "__main__":
    main()
