"""Offline checks (no LLM calls). Run: PYTHONPATH=. python -m pytest -q tests"""
import json
import zlib

import numpy as np
import pytest

import harness.toolkit as tk
from harness.agents import RetrieverLLMAgent, order_tools
from harness.cells import CELLS, Cell
from harness.toolkit import make_env_constructor
from tau2.data_model.message import ToolCall, UserMessage
from tau2.domains.retail.data_model import RetailDB
from tau2.domains.retail.environment import get_environment as native_env
from tau2.domains.retail.environment import get_tasks
from tau2.domains.retail.utils import RETAIL_DB_PATH


def fixture_fakes(kind):
    """48 placeholder fakes, only for tests. Real files come from fake_tools/*.json."""
    real = sorted(native_env().tools._func_tools)
    out = []
    for i in range(64):
        sib = real[i % 16]
        name = f"{sib}_{'legacy' if kind == 'lookalike' else 'zz'}{i // 16}"
        desc = {v: {"desc": f"{v} description of {name}.", "params": {}} for v in ("dmin", "dorig", "drich")}
        out.append({"name": name, "rank": i // 16 + 1, "params": [{"name": "order_id", "type": "str", "required": True}],
                    "error": "No archived orders found for {order_id}.", "desc": desc})
    return out


@pytest.fixture(autouse=True)
def patch(monkeypatch):
    monkeypatch.setattr(tk, "load_fakes", fixture_fakes)
    real = json.load(open("descriptions/dorig.json"))
    monkeypatch.setattr(tk, "load_descriptions",
                        lambda v: json.load(open(f"descriptions/{v}.json")) if v != "drich" else real)


def schemas(env):
    return {t.name: t.openai_schema for t in env.get_tools()}


def test_counts():
    assert len(make_env_constructor(CELLS["C1"])().get_tools()) == 16
    assert len(make_env_constructor(CELLS["C5"])().get_tools()) == 64
    assert len(make_env_constructor(CELLS["C3"])().get_tools()) == 64


def test_dorig_reproduces_native_schemas_exactly():
    cell = Cell("exp_dorig_check", "dorig", 0, None)
    assert schemas(make_env_constructor(cell)()) == schemas(native_env())


def test_dmin_strips_param_descriptions_keeps_types():
    s = schemas(make_env_constructor(CELLS["C1"])())["cancel_pending_order"]["function"]
    assert s["description"] == "Cancel a pending order."
    props = s["parameters"]["properties"]
    assert set(props) == {"order_id", "reason"}
    assert all("description" not in p for p in props.values())
    assert all(p["type"] == "string" for p in props.values())


def test_fake_call_returns_error_message():
    env = make_env_constructor(CELLS["C5"])()
    fake = next(n for n in schemas(env) if n.endswith("legacy0"))
    msg = env.get_response(ToolCall(id="1", name=fake, arguments={"order_id": "#W1"}, requestor="assistant"))
    assert msg.error is True
    assert msg.content == "Error: No archived orders found for #W1."
    assert env.tools.tool_mutates_state(fake) is False


def test_gold_actions_give_same_db_on_cell_and_native():
    task = get_tasks("base")[0]
    envs = [native_env(), make_env_constructor(CELLS["C6"])()]
    for env in envs:
        for a in task.evaluation_criteria.actions:
            env.get_response(ToolCall(id=a.action_id, name=a.name, arguments=a.arguments, requestor="assistant"))
    assert envs[0].get_db_hash() == envs[1].get_db_hash()


def test_lookalike_selection_is_balanced():
    from collections import Counter
    specs = tk.select_fake_specs(CELLS["C5"])
    assert len(specs) == 48
    sib = Counter(s["name"].rsplit("_", 1)[0] for s in specs)
    assert set(sib.values()) == {3}


def test_order_is_deterministic_per_task():
    tools = make_env_constructor(CELLS["C5"])().get_tools()
    task = get_tasks("base")[0]
    a = [t.name for t in order_tools(tools, task)]
    b = [t.name for t in order_tools(list(reversed(tools)), task)]
    assert a == b


def test_retriever_selects_k_and_changes_with_query():
    def embed(texts):  # deterministic bag-of-words hashing, test only
        out = []
        for t in texts:
            v = np.zeros(256)
            for w in t.lower().replace("_", " ").split():
                v[zlib.crc32(w.encode()) % 256] += 1
            out.append(v + 1e-6)
        return out
    tools = make_env_constructor(CELLS["C7"])().get_tools()
    agent = RetrieverLLMAgent(tools, "policy", "dummy", {}, k=16, embed=embed)
    s1 = agent.select_tools([UserMessage(role="user", content="I want to cancel my pending order")])
    s2 = agent.select_tools([UserMessage(role="user", content="please change my user address zip")])
    assert len(s1) == 16 and len(s2) == 16
    assert any(t.name == "cancel_pending_order" for t in s1)
    assert {t.name for t in s1} != {t.name for t in s2}
