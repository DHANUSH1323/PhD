"""Retail toolkit with swapped descriptions and injected fake tools."""
import random
from typing import Optional

from tau2.domains.retail.data_model import RetailDB
from tau2.domains.retail.tools import RetailTools
from tau2.domains.retail.utils import RETAIL_DB_PATH, RETAIL_POLICY_PATH
from tau2.environment.environment import Environment
from tau2.environment.tool import as_tool

from harness.cells import Cell
from harness.fakes import build_fake, load_fakes
from harness.variants import load_descriptions, make_doc, with_doc

FAKE_ORDER_SEED = 2026  # fixed: which fakes are used when fewer than the full pool


def select_fake_specs(cell: Cell) -> list[dict]:
    if cell.n_fakes == 0:
        return []
    pool = sorted(load_fakes(cell.fake_kind), key=lambda s: s["name"])
    random.Random(FAKE_ORDER_SEED).shuffle(pool)
    if all("rank" in s for s in pool):
        # look-alikes: all rank-1 siblings first, then rank 2, ... so every real
        # tool gets the same number of look-alikes (16 -> 1 each, 48 -> 3 each)
        pool.sort(key=lambda s: s["rank"])  # stable: keeps the seeded order within a rank
    if cell.n_fakes > len(pool):
        raise ValueError(f"Pool {cell.fake_kind} has {len(pool)} tools, need {cell.n_fakes}")
    return pool[: cell.n_fakes]


class ExperimentRetailTools(RetailTools):
    def __init__(self, db: RetailDB, cell: Cell) -> None:
        super().__init__(db)
        self.cell = cell
        docs = load_descriptions(cell.variant)
        real = {name: getattr(self, name) for name in self._func_tools.keys()}
        missing = set(real) - set(docs)
        if missing:
            raise ValueError(f"{cell.variant}.json lacks: {sorted(missing)}")
        self._real = {n: with_doc(fn, make_doc(docs[n])) for n, fn in real.items()}
        self._fakes = {s["name"]: build_fake(s, cell.variant) for s in select_fake_specs(cell)}
        clash = set(self._real) & set(self._fakes)
        if clash:
            raise ValueError(f"Fake tool names collide with retail tools: {sorted(clash)}")

    @property
    def tools(self):
        return {**self._real, **self._fakes}

    def get_tools(self, include: Optional[list[str]] = None):
        tools = {name: as_tool(fn) for name, fn in self.tools.items()}
        if include is not None:
            tools = {n: t for n, t in tools.items() if n in set(include)}
        return tools

    def is_fake(self, name: str) -> bool:
        return name in self._fakes


def make_env_constructor(cell: Cell):
    def get_environment(db: Optional[RetailDB] = None, solo_mode: bool = False, **kwargs) -> Environment:
        if solo_mode:
            raise ValueError("Retail does not support solo mode")
        if db is None:
            db = RetailDB.load(RETAIL_DB_PATH)
        with open(RETAIL_POLICY_PATH) as fp:
            policy = fp.read()
        return Environment(domain_name=cell.name, policy=policy,
                           tools=ExperimentRetailTools(db, cell))
    return get_environment
