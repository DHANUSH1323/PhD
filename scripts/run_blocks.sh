#!/usr/bin/env bash
# Spec 8.9 main loop: trial blocks, each block = all 11 cells in the fixed order (rule 16),
# every run logged by scripts/run_logged.sh. Stops at the first failing cell (rerun to resume:
# completed (trial, task, seed) runs are skipped by run_cell).
# Models come from models.env (repo root); environment variables override it.
# Usage: caffeinate -i scripts/run_blocks.sh [first_trial] [last_trial]
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f models.env ] && set -a && source models.env && set +a
: "${AGENT:?set AGENT}"; : "${USER_LLM:?set USER_LLM}"; : "${RETRIEVER:?set RETRIEVER}"
FIRST="${1:-1}"; LAST="${2:-${TRIALS:-3}}"
for T in $(seq "$FIRST" "$LAST"); do
  for C in C1 C5 C10 C3 C6 C11 C4 C2 C9 C7 C8; do
    EXTRA=(); case $C in C7|C8) EXTRA=(--retriever-embed "$RETRIEVER");; esac
    scripts/run_logged.sh "$C" "$T" main "$AGENT" "$USER_LLM" "${EXTRA[@]}"
  done
  echo "=== block $T complete $(date '+%Y-%m-%d %H:%M:%S')" | tee -a logs/blocks.log
done
