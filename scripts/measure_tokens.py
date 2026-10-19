"""Schema and policy tokens per cell (o200k_base). Writes results/tokens.csv.

Usage: python scripts/measure_tokens.py [--cells C1 C2 ...]
"""
import argparse
import csv
import json
from pathlib import Path

from harness.cells import CELLS, get_cell
from harness.toolkit import make_env_constructor

OUT = Path(__file__).resolve().parent.parent / "results" / "tokens.csv"


def get_encoder():
    import tiktoken
    return tiktoken.get_encoding("o200k_base")


def schema_tokens(cell, enc) -> int:
    env = make_env_constructor(cell)()
    return sum(len(enc.encode(json.dumps(t.openai_schema))) for t in env.get_tools())


def policy_tokens(cell, enc) -> int:
    return len(enc.encode(make_env_constructor(cell)().get_policy()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", nargs="*", default=list(CELLS))
    ap.add_argument("--include-dorig", action="store_true",
                    help="add a 16-tool dorig row; it should match the Step 1 measurement (3,188)")
    a = ap.parse_args()
    enc = get_encoder()
    rows = []
    from harness.cells import Cell
    keys = a.cells + (["DORIG16"] if a.include_dorig else [])
    for key in keys:
        cell = Cell("exp_dorig16", "dorig", 0, None) if key == "DORIG16" else get_cell(key)
        n = len(make_env_constructor(cell)().get_tools())
        rows.append({"cell": key, "tools": n, "schema_tokens": schema_tokens(cell, enc),
                     "policy_tokens": policy_tokens(cell, enc)})
        print(rows[-1])
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
