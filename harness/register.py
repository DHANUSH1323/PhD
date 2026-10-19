"""Register a cell's domain and agent with the tau2 registry."""
from tau2.registry import registry

from harness.agents import create_llm_agent_exp, make_retriever_factory
from harness.cells import Cell
from harness.toolkit import make_env_constructor


def register_cell(cell: Cell, embedder=None) -> str:
    """Registers the cell's domain; returns the agent name to use."""
    if cell.name not in registry.get_domains():
        registry.register_domain(make_env_constructor(cell), cell.name)
    if cell.retriever_k is None:
        agent_name = "llm_agent_exp"
        if agent_name not in registry.get_agents():
            registry.register_agent_factory(create_llm_agent_exp, agent_name)
    else:
        if embedder is None:
            raise ValueError("Retriever cells need an embedder")
        agent_name = f"llm_agent_retriever_k{cell.retriever_k}"
        if agent_name not in registry.get_agents():
            registry.register_agent_factory(make_retriever_factory(cell.retriever_k, embedder), agent_name)
    return agent_name
