"""Count tau2's truncation warning per log file.

tau2 prints "Output might be incomplete due to token limit!" (src/tau2/utils/llm_utils.py)
whenever a model reply stops because it hit the output-token limit. One line per cut-off reply.
Usage: python scripts/count_truncation.py [logs/*.log]   -> table per cell/trial, totals, and
       any Python tracebacks seen (a crash signature), so a night run can be checked in one look.
"""
import re
import sys
from pathlib import Path

WARN = "Output might be incomplete due to token limit!"
ROOT = Path(__file__).resolve().parent.parent


def main():
    files = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / "logs").glob("*_T*.log"))
    if not files:
        print("no log files found in logs/"); return
    print(f"{'log':20s} {'truncations':>11s} {'tracebacks':>10s} {'runs started':>12s} {'runs ended':>10s}")
    tot_w = tot_tb = 0
    for f in files:
        text = f.read_text(errors="replace")
        w = text.count(WARN); tb = text.count("Traceback (most recent call last)")
        starts = len(re.findall(r"^=== .* start cell=", text, re.M)); ends = len(re.findall(r"^=== .* end cell=", text, re.M))
        tot_w += w; tot_tb += tb
        print(f"{f.name:20s} {w:11d} {tb:10d} {starts:12d} {ends:10d}")
    print(f"{'TOTAL':20s} {tot_w:11d} {tot_tb:10d}")


if __name__ == "__main__":
    main()
