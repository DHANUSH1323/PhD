"""The nine pre-registered cells."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Cell:
    name: str
    variant: str               # dmin | dorig | drich
    n_fakes: int               # fake tools added to the 16 real ones
    fake_kind: Optional[str]   # lookalike | unrelated | None
    retriever_k: Optional[int] = None   # None = agent sees every tool


C9_N_FAKES = None  # set on Oct 15 from the token measurement; see scripts/set_c9.py

CELLS = {
    "C1": Cell("exp_C1", "dmin", 0, None),
    "C2": Cell("exp_C2", "drich", 0, None),
    "C3": Cell("exp_C3", "dmin", 48, "unrelated"),
    "C4": Cell("exp_C4", "drich", 48, "unrelated"),
    "C5": Cell("exp_C5", "dmin", 48, "lookalike"),
    "C6": Cell("exp_C6", "drich", 48, "lookalike"),
    "C7": Cell("exp_C7", "dmin", 48, "lookalike", retriever_k=16),
    "C8": Cell("exp_C8", "drich", 48, "lookalike", retriever_k=16),
}


def get_cell(key: str) -> Cell:
    if key == "C9":
        if C9_N_FAKES is None:
            raise ValueError("C9_N_FAKES not set yet (Oct 15 step).")
        return Cell("exp_C9", "dmin", C9_N_FAKES, "lookalike")
    return CELLS[key]
