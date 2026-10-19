"""Find N look-alikes so that C9 (dmin, 16 + N tools) matches C2's schema tokens within 5%.

Prints N and both totals. Then set C9_N_FAKES = N in harness/cells.py by hand and commit.
"""
from harness.cells import CELLS, Cell
from harness.fakes import load_fakes
from scripts.measure_tokens import get_encoder, schema_tokens


def find_n(enc, max_n):
    target = schema_tokens(CELLS["C2"], enc)
    best = None
    for n in range(0, max_n + 1):
        tok = schema_tokens(Cell("exp_C9", "dmin", n, "lookalike"), enc)
        if best is None or abs(tok - target) < abs(best[1] - target):
            best = (n, tok)
        if tok >= target:
            break
    return target, best


def main():
    enc = get_encoder()
    max_n = len(load_fakes("lookalike"))
    target, (n, tok) = find_n(enc, max_n)
    gap = (tok - target) / target
    print(f"C2 schema tokens: {target}; C9 with N={n}: {tok} ({gap:+.1%})")
    if abs(gap) > 0.05:
        raise SystemExit("Gap above 5%: the look-alike pool is too small. Add a 5th look-alike per tool (rank 5) and rerun.")


if __name__ == "__main__":
    main()
