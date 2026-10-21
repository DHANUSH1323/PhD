"""Checks on the real fake_tools/unrelated.json and results/similarity.csv (no LLM calls)."""
import csv
import json
from collections import Counter

import pytest

from harness.cells import CELLS
from harness.fakes import build_fake
from harness.toolkit import make_env_constructor
from tau2.domains.retail.environment import get_environment as native_env

SPECS = json.load(open("fake_tools/unrelated.json"))
LOOKALIKES = json.load(open("fake_tools/lookalike.json"))
REAL = {t.name for t in native_env().get_tools()}


def test_file_shape():
    names = [s["name"] for s in SPECS]
    assert len(SPECS) == 48 and len(set(names)) == 48
    assert not set(names) & REAL
    assert not set(names) & {s["name"] for s in LOOKALIKES}
    assert all(s["kind"] == "unrelated" and s["sibling"] is None for s in SPECS)
    assert all(s["desc"]["dmin"]["desc"] and s["desc"]["dorig"]["desc"] for s in SPECS)


@pytest.mark.parametrize("spec", SPECS, ids=[s["name"] for s in SPECS])
def test_builds_and_errors(spec):
    fn = build_fake(spec, "dorig")
    args = {p["name"]: "x" for p in spec["params"] if p["required"]}
    with pytest.raises(ValueError, match="The request could not be completed."):
        fn(**args)


def test_ladder_order_in_similarity_csv():
    rows = list(csv.DictReader(open("results/similarity.csv")))
    by = {}
    for r in rows:
        by.setdefault(r["kind"], []).append(float(r["max_sim_to_real"]))
    assert len(by["lookalike"]) == 48 and len(by["indomain"]) == 48 and len(by["unrelated"]) == 48
    assert min(by["lookalike"]) > max(by["unrelated"])
    import statistics as st
    assert st.median(by["lookalike"]) > st.median(by["indomain"]) > st.median(by["unrelated"])


def test_no_shop_flavoured_unrelated():
    from scripts.similarity_check import shop_flavoured
    assert not [s["name"] for s in SPECS if shop_flavoured(s)]


def test_c3_env_has_64_tools():
    env = make_env_constructor(CELLS["C3"])()
    tools = env.get_tools()
    assert len(tools) == 64
    assert Counter(env.tools.is_fake(t.name) for t in tools) == {True: 48, False: 16}
