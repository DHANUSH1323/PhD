"""Agents: fixed tool order per task, and the per-turn retriever agent."""
import random
from typing import Callable

import numpy as np

from tau2.agent.llm_agent import LLMAgent
from tau2.data_model.message import UserMessage


def order_tools(tools, task):
    tools = sorted(tools, key=lambda t: t.name)
    random.Random(str(task.id)).shuffle(tools)
    return tools


def tool_text(tool) -> str:
    schema = tool.openai_schema["function"]
    params = " ".join(schema["parameters"].get("properties", {}).keys())
    return f"{schema['name']} {schema['description']} {params}"


def create_llm_agent_exp(tools, domain_policy, **kwargs):
    return LLMAgent(tools=order_tools(tools, kwargs["task"]), domain_policy=domain_policy,
                    llm=kwargs.get("llm"), llm_args=kwargs.get("llm_args"))


class RetrieverLLMAgent(LLMAgent):
    """Shows the agent only the top-k tools for the conversation so far."""

    QUERY_CHARS = 2000

    def __init__(self, tools, domain_policy, llm, llm_args, k: int, embed: Callable):
        super().__init__(tools=tools, domain_policy=domain_policy, llm=llm, llm_args=llm_args)
        self.all_tools = list(tools)
        self.k = k
        self.embed = embed
        mat = np.asarray(embed([tool_text(t) for t in self.all_tools]), dtype=float)
        self.tool_mat = mat / np.linalg.norm(mat, axis=1, keepdims=True)

    def select_tools(self, messages) -> list:
        text = " ".join(m.content for m in messages
                        if isinstance(m, UserMessage) and m.content)[-self.QUERY_CHARS:]
        if not text.strip():
            return self.all_tools[: self.k]
        q = np.asarray(self.embed([text])[0], dtype=float)
        q = q / np.linalg.norm(q)
        scores = self.tool_mat @ q
        top = set(np.argsort(-scores, kind="stable")[: self.k].tolist())
        return [t for i, t in enumerate(self.all_tools) if i in top]  # keep fixed order

    def _generate_next_message(self, message, state):
        history = list(state.messages) + [message]
        self.tools = self.select_tools(history)
        return super()._generate_next_message(message, state)


def make_retriever_factory(k: int, embed: Callable):
    def factory(tools, domain_policy, **kwargs):
        return RetrieverLLMAgent(order_tools(tools, kwargs["task"]), domain_policy,
                                 kwargs.get("llm"), kwargs.get("llm_args"), k, embed)
    return factory
