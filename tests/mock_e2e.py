"""End-to-end run of one cell with scripted (mock) LLMs: no API calls.
Checks that registration, simulation, fake-tool errors, grading and saving all work."""
import itertools

import tau2.agent.llm_agent as la
import tau2.user.user_simulator as us
import harness.toolkit as tk
from tau2.data_model.message import AssistantMessage, ToolCall, ToolMessage, UserMessage
from tau2.data_model.simulation import TextRunConfig
from tau2.runner.batch import run_domain
from tau2.user.user_simulator import STOP

from harness.cells import CELLS
from harness.register import register_cell
from tests.test_harness import fixture_fakes

tk.load_fakes = fixture_fakes
ids = itertools.count()

def agent_generate(model, messages, tools=None, **kw):
    names = {t.name for t in tools}
    tool_msgs = [m for m in messages if isinstance(m, ToolMessage)]
    fake = next(n for n in sorted(names) if n.endswith("legacy0"))
    if not tool_msgs:
        tc = ToolCall(id=f"c{next(ids)}", name=fake, arguments={"order_id": "#W2378156"}, requestor="assistant")
        return AssistantMessage(role="assistant", content=None, tool_calls=[tc])
    if len(tool_msgs) == 1:
        tc = ToolCall(id=f"c{next(ids)}", name="get_order_details", arguments={"order_id": "#W2378156"}, requestor="assistant")
        return AssistantMessage(role="assistant", content=None, tool_calls=[tc])
    return AssistantMessage(role="assistant", content="Your order is delivered.")

def user_generate(model, messages, tools=None, **kw):
    n_user_turns = sum(1 for m in messages if m.role == "assistant")
    return UserMessage(role="user", content="Hi, what is the status of order #W2378156?" if n_user_turns <= 1 else STOP)

la.generate = agent_generate
us.generate = user_generate

cell = CELLS["C5"]
agent = register_cell(cell)
cfg = TextRunConfig(domain=cell.name, task_set_name="retail", task_split_name="base", task_ids=["0"],
                    agent=agent, llm_agent="mock", llm_args_agent={}, user="user_simulator", llm_user="mock",
                    llm_args_user={}, num_trials=1, seed=300, max_concurrency=1, hallucination_retries=0,
                    auto_resume=True, save_to=str(__import__("pathlib").Path(__file__).resolve().parent.parent / "results" / "raw" / "mock__exp_C5"))
res = run_domain(cfg)
sim = res.simulations[0]
print("termination:", sim.termination_reason, "reward:", sim.reward_info.reward if sim.reward_info else None)
for m in sim.messages:
    if getattr(m, "tool_calls", None): print("CALL", [tc.name for tc in m.tool_calls])
    if m.role == "tool": print("TOOL", m.error, str(m.content)[:70])
