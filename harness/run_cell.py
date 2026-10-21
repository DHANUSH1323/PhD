"""Run one cell.

Example:
  python -m harness.run_cell --cell C5 --agent-llm <AGENT_MODEL> --user-llm <USER_MODEL> \
      --trials 3 --concurrency 3 [--task-ids 0 1 2] [--retriever-embed st:sentence-transformers/all-MiniLM-L6-v2]

Trial blocks: run every cell with --trials 1, then every cell with --trials 2, then --trials 3.
Per-trial seeds are a prefix-stable list drawn from SEED, and auto_resume skips (trial, task, seed)
already done, so each pass adds exactly one new trial per task.
"""
import argparse
import hashlib
import json
from pathlib import Path

from tau2.data_model.simulation import TextRunConfig
from tau2.runner.batch import run_domain

from harness.cells import get_cell
from harness.register import register_cell

SEED = 300  # identical in every cell: this is what pairs the cells
RAW = Path(__file__).resolve().parent.parent / "results" / "raw"  # absolute path: tau2 saves here, not inside the submodule


def fake_files_hash() -> str:
    """Hash of descriptions/ and fake_tools/ so a resumed run cannot silently mix file versions."""
    root = RAW.parent.parent
    h = hashlib.sha256()
    for d in ("descriptions", "fake_tools"):
        for f in sorted((root / d).glob("*.json")):
            h.update(f.name.encode() + f.read_bytes())
    return h.hexdigest()[:16]


def check_meta(save_to: str, meta: dict) -> None:
    """tau2's auto_resume only warns when the config changes. Stop instead if anything but
    the trial count differs from the first run saved under this name."""
    path = Path(save_to + ".meta.json")
    if path.exists():
        old = json.loads(path.read_text())
        diff = {k: (old.get(k), v) for k, v in meta.items() if old.get(k) != v}
        if diff:
            raise SystemExit(f"Refusing to resume {save_to}: settings differ from the first run: {diff}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(meta, indent=2))


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
    check_meta(config.save_to, {"agent_llm": a.agent_llm, "user_llm": a.user_llm,
                                "retriever_embed": a.retriever_embed, "task_ids": a.task_ids,
                                "n_fakes": cell.n_fakes, "files": fake_files_hash()})
    run_domain(config)


if __name__ == "__main__":
    main()
