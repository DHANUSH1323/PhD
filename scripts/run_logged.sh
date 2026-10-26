#!/usr/bin/env bash
# Run one cell for one trial and keep everything it prints in logs/<cell>_T<trial>.log
# (tau2 warns "Output might be incomplete due to token limit!" when a reply is cut off;
#  scripts/count_truncation.py counts those lines per cell afterwards).
# Usage: scripts/run_logged.sh <cell> <trial> <tag> <agent-llm> <user-llm> [extra run_cell args...]
set -o pipefail
CELL="$1"; TRIAL="$2"; TAG="$3"; AGENT="$4"; USER_LLM="$5"; shift 5
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
LOG="logs/${CELL}_T${TRIAL}.log"
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') start cell=$CELL trial=$TRIAL tag=$TAG agent=$AGENT user=$USER_LLM extra=$*"
  PYTHONPATH=. python -m harness.run_cell --cell "$CELL" --agent-llm "$AGENT" --user-llm "$USER_LLM" \
      --trials "$TRIAL" --concurrency "${CONCURRENCY:-3}" --tag "$TAG" "$@" 2>&1
  STATUS=$?
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') end cell=$CELL trial=$TRIAL exit=$STATUS"
  exit $STATUS
} | tee -a "$LOG"
