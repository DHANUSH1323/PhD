"""Checks on the real fake_tools/lookalike.json (no fixtures, no LLM calls)."""
import json
from collections import Counter

import pytest

from harness.cells import CELLS
from harness.fakes import build_fake
from harness.toolkit import make_env_constructor, select_fake_specs
from tau2.data_model.message import ToolCall
from tau2.domains.retail.environment import get_environment as native_env
from tau2.environment.tool import as_tool

SPECS = json.load(open("fake_tools/lookalike.json"))
REAL = {t.name: t for t in native_env().get_tools()}


def params_without_descriptions(schema):
    p = json.loads(json.dumps(schema["function"]["parameters"]))
    for prop in p.get("properties", {}).values():
        prop.pop("description", None)
    return p


def test_file_shape():
    names = [s["name"] for s in SPECS]
    assert len(SPECS) == 64 and len(set(names)) == 64
    assert not set(names) & set(REAL)
    assert Counter(s["rank"] for s in SPECS) == {1: 16, 2: 16, 3: 16, 4: 16}
    assert Counter(s["sibling"] for s in SPECS) == {n: 4 for n in REAL}
    assert all(s["desc"]["dmin"]["desc"] and s["desc"]["dorig"]["desc"] for s in SPECS)
    assert all(s["desc"]["dmin"]["params"] == {} for s in SPECS)


@pytest.mark.parametrize("spec", SPECS, ids=[s["name"] for s in SPECS])
def test_parameters_identical_to_sibling(spec):
    fake = as_tool(build_fake(spec, "dorig"))
    assert params_without_descriptions(fake.openai_schema) == params_without_descriptions(REAL[spec["sibling"]].openai_schema)


def test_errors_render_and_never_name_a_real_tool():
    for spec in SPECS:
        fn = build_fake(spec, "dorig")
        args = {p["name"]: "x" for p in spec["params"]}
        with pytest.raises(ValueError) as e:
            fn(**args)
        msg = str(e.value)
        assert msg and "{" not in msg
        assert not any(real in msg for real in REAL), spec["name"]


def test_c5_uses_ranks_1_to_3_balanced():
    specs = select_fake_specs(CELLS["C5"])
    assert len(specs) == 48
    assert Counter(s["sibling"] for s in specs) == {n: 3 for n in REAL}
    assert set(s["rank"] for s in specs) == {1, 2, 3}


def test_c5_env_has_64_tools_and_fakes_error_through_tau2():
    env = make_env_constructor(CELLS["C5"])()
    assert len(env.get_tools()) == 64
    msg = env.get_response(ToolCall(id="1", name="get_order_details_archived",
                                    arguments={"order_id": "#W1"}, requestor="assistant"))
    assert msg.error is True
    assert msg.content == "Error: No archived record matches this request."
