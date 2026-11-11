"""Provider-counted prompt tokens for a cell's first agent request (Amendment 2).

tokens.csv counted tiktoken over json.dumps(openai_schema); the provider serializes tool schemas
differently, so block-1 C9 (sized to C2 within 0.3% by tiktoken) actually sent 5,088 vs 8,276
prompt tokens. This script sends the exact first request the agent would send (tau2 system prompt
with the cell's policy, the cell's tools, one fixed user line) with max_tokens=1 and reads
usage.prompt_tokens from the provider. Cost: about 8k input tokens per cell, well under a cent.

Usage: AGENT=gpt-4.1-mini-2025-04-14 python scripts/measure_provider_tokens.py C1 C2 C9 C12 C14n28 C14n32 C14n36
"""
import os
import sys

import litellm

from harness.cells import get_cell
from harness.toolkit import make_env_constructor
from tau2.agent.llm_agent import AGENT_INSTRUCTION, SYSTEM_PROMPT

USER_LINE = "Hi, I need help with one of my orders."


def provider_prompt_tokens(key: str, model: str) -> tuple[int, int]:
    cell = get_cell(key)
    env = make_env_constructor(cell)()
    tools = [t.openai_schema for t in env.get_tools()]
    system = SYSTEM_PROMPT.format(domain_policy=env.get_policy(), agent_instruction=AGENT_INSTRUCTION)
    r = litellm.completion(model=model, temperature=0.0, max_tokens=1, tools=tools,
                           messages=[{"role": "system", "content": system},
                                     {"role": "user", "content": USER_LINE}])
    return len(tools), r.usage.prompt_tokens


def main():
    model = os.environ.get("AGENT")
    if not model:
        raise SystemExit("set AGENT (see models.env)")
    for key in sys.argv[1:]:
        n, tok = provider_prompt_tokens(key, model)
        print(f"{key}: {n} tools, provider prompt_tokens = {tok}")


if __name__ == "__main__":
    main()
