"""Checks on the real fake_tools/indomain.json (no LLM calls)."""
import json
from collections import Counter

import pytest

from harness.cells import CELLS
from harness.fakes import build_fake
from harness.toolkit import make_env_constructor
from tau2.data_model.message import ToolCall
from tau2.domains.retail.environment import get_environment as native_env

SPECS = json.load(open("fake_tools/indomain.json"))
LOOKALIKES = json.load(open("fake_tools/lookalike.json"))
REAL = {t.name: t for t in native_env().get_tools()}
REAL_PARAM_SETS = [set(t.openai_schema["function"]["parameters"].get("properties", {})) for t in REAL.values()]


def test_file_shape():
    names = [s["name"] for s in SPECS]
    assert len(SPECS) == 48 and len(set(names)) == 48
    assert not set(names) & set(REAL)
    assert not set(names) & {s["name"] for s in LOOKALIKES}
    assert all(s["kind"] == "indomain" and s["sibling"] is None and "rank" not in s for s in SPECS)
    assert all(s["desc"]["dmin"]["desc"] and s["desc"]["dorig"]["desc"] for s in SPECS)
    assert all(s["desc"]["dmin"]["params"] == {} for s in SPECS)
    assert all(p["required"] for s in SPECS for p in s["params"])


def test_no_parameter_set_equals_a_real_tool():
    for s in SPECS:
        assert {p["name"] for p in s["params"]} not in REAL_PARAM_SETS, s["name"]


@pytest.mark.parametrize("spec", SPECS, ids=[s["name"] for s in SPECS])
def test_builds_and_errors(spec):
    fn = build_fake(spec, "dorig")
    args = {p["name"]: "x" for p in spec["params"]}
    with pytest.raises(ValueError, match="This service is currently unavailable."):
        fn(**args)


def test_c10_env_has_64_tools_and_fake_errors_through_tau2():
    env = make_env_constructor(CELLS["C10"])()
    tools = env.get_tools()
    assert len(tools) == 64
    assert Counter(env.tools.is_fake(t.name) for t in tools) == {True: 48, False: 16}
    msg = env.get_response(ToolCall(id="1", name="apply_coupon_code",
                                    arguments={"user_id": "u", "coupon_code": "SAVE10"}, requestor="assistant"))
    assert msg.error is True
    assert msg.content == "Error: This service is currently unavailable."
