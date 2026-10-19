"""Run one cell.

Example:
  python -m harness.run_cell --cell C5 --agent-llm <AGENT_MODEL> --user-llm <USER_MODEL> \
      --trials 3 --concurrency 3 [--task-ids 0 1 2] [--retriever-embed st:sentence-transformers/all-MiniLM-L6-v2]
"""
import argparse
from pathlib import Path

from tau2.data_model.simulation import TextRunConfig
from tau2.runner.batch import run_domain

from harness.cells import get_cell
from harness.register import register_cell

SEED = 300  # identical in every cell: this is what pairs the cells
RAW = Path(__file__).resolve().parent.parent / "results" / "raw"  # absolute path: tau2 saves here, not inside the submodule


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", required=True)
    ap.add_argument("--agent-llm", required=True)
    ap.add_argument("--user-llm", required=True)
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--task-ids", nargs="*", default=None)
    ap.add_argument("--retriever-embed", default=None)
    ap.add_argument("--tag", default="main", help="'pilot' or 'main'; part of the save name")
    a = ap.parse_args()

    cell = get_cell(a.cell)
    embedder = None
    if cell.retriever_k is not None:
        from harness.embed import get_embedder
        embedder = get_embedder(a.retriever_embed)
    agent_name = register_cell(cell, embedder)

    config = TextRunConfig(
        domain=cell.name,
        task_set_name="retail",
        task_split_name="base",
        task_ids=a.task_ids,
        agent=agent_name,
        llm_agent=a.agent_llm,
        llm_args_agent={"temperature": 0.0},
        user="user_simulator",
        llm_user=a.user_llm,
        llm_args_user={"temperature": 0.0},
        num_trials=a.trials,
        seed=SEED,
        max_steps=200,
        max_errors=10,
        max_concurrency=a.concurrency,
        hallucination_retries=0,
        auto_resume=True,
        save_to=str(RAW / f"{a.tag}__{cell.name}__{a.agent_llm.replace('/', '_')}"),
    )
    run_domain(config)


if __name__ == "__main__":
    main()
