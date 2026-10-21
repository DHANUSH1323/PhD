"""The eleven pre-registered cells.

Fake-tool kinds, from farthest to closest to the real retail tools:
  unrelated  = cross-domain tools from other services (C3, C4)
  indomain   = other retail functions that no task needs (C10, C11)
  lookalike  = near-copies of real retail tools (C5 to C9)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Cell:
    name: str
    variant: str               # dmin | dorig | drich
    n_fakes: int               # fake tools added to the 16 real ones
    fake_kind: Optional[str]   # unrelated | indomain | lookalike | None
    retriever_k: Optional[int] = None   # None = agent sees every tool


C9_N_FAKES = None  # set from the token measurement (scripts/set_c9.py), then committed

CELLS = {
    "C1": Cell("exp_C1", "dmin", 0, None),
    "C2": Cell("exp_C2", "drich", 0, None),
    "C3": Cell("exp_C3", "dmin", 48, "unrelated"),
    "C4": Cell("exp_C4", "drich", 48, "unrelated"),
    "C5": Cell("exp_C5", "dmin", 48, "lookalike"),
    "C6": Cell("exp_C6", "drich", 48, "lookalike"),
    "C7": Cell("exp_C7", "dmin", 48, "lookalike", retriever_k=16),
    "C8": Cell("exp_C8", "drich", 48, "lookalike", retriever_k=16),
    "C10": Cell("exp_C10", "dmin", 48, "indomain"),
    "C11": Cell("exp_C11", "drich", 48, "indomain"),
}


def get_cell(key: str) -> Cell:
    if key == "C9":
        if C9_N_FAKES is None:
            raise ValueError("C9_N_FAKES not set yet (token measurement step).")
        return Cell("exp_C9", "dmin", C9_N_FAKES, "lookalike")
    return CELLS[key]
