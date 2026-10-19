"""One row per conversation from tau2 results files.

Usage: python -m analysis.extract <results.json> [<results.json> ...] --out runs.csv
"""
import argparse
import csv
import json

from harness.cells import CELLS, get_cell
from harness.toolkit import make_env_constructor

CELL_BY_NAME = {c.name: k for k, c in CELLS.items()}


def fake_names_for(domain_name: str) -> set:
    key = CELL_BY_NAME.get(domain_name) or ("C9" if domain_name == "exp_C9" else None)
    if key is None:
        return set()
    env = make_env_constructor(get_cell(key))()
    return {n for n in env.tools.tools if env.tools.is_fake(n)}


def rows_from(path: str):
    d = json.load(open(path))
    domain = d["info"]["environment_info"]["domain_name"]
    fakes = fake_names_for(domain)
    for s in d["simulations"]:
        msgs = s["messages"]
        calls = [(i, tc["name"]) for i, m in enumerate(msgs) for tc in (m.get("tool_calls") or [])]
        tool_msgs = [m for m in msgs if m["role"] == "tool"]
        fake_calls = [(i, n) for i, n in calls if n in fakes]
        first_fake = fake_calls[0][0] if fake_calls else None
        real_after_fake = any(i > first_fake and n not in fakes for i, n in calls) if fake_calls else None
        ri = s.get("reward_info") or {}
        usage = [m.get("usage") or {} for m in msgs if m["role"] == "assistant"]
        yield {
            "cell": domain, "task_id": s["task_id"], "trial": s["trial"], "seed": s["seed"],
            "reward": ri.get("reward"),
            "db_match": (ri.get("db_check") or {}).get("db_match"),
            "reward_breakdown": json.dumps(ri.get("reward_breakdown")),
            "termination": s["termination_reason"],
            "n_messages": len(msgs),
            "n_agent_turns": sum(m["role"] == "assistant" for m in msgs),
            "n_tool_calls": len(calls),
            "n_fake_calls": len(fake_calls),
            "first_fake_tool": fake_calls[0][1] if fake_calls else "",
            "real_tool_after_fake": real_after_fake,
            "n_tool_errors": sum(bool(m.get("error")) for m in tool_msgs),
            "n_real_tool_errors": sum(bool(m.get("error")) for m in tool_msgs) - len(fake_calls),
            "agent_input_tokens": sum((u.get("prompt_tokens") or 0) for u in usage),
            "agent_output_tokens": sum((u.get("completion_tokens") or 0) for u in usage),
            "agent_cost": s.get("agent_cost"), "user_cost": s.get("user_cost"),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = [r for p in a.paths for r in rows_from(p)]
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {a.out}")


if __name__ == "__main__":
    main()
