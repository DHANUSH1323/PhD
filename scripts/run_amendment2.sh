#!/usr/bin/env bash
# Amendment 2 cells, one trial each, in order. Models from models.env; key from benchmarks/tau2-bench/.env.
# Usage: caffeinate -i scripts/run_amendment2.sh
set -uo pipefail
cd "$(dirname "$0")/.."
set -a; source benchmarks/tau2-bench/.env; source models.env; set +a
for C in C12 C14 C13 C15; do
  EXTRA=(); case $C in C13|C15) EXTRA=(--concurrency 3);; C14) EXTRA=(--concurrency 3);; esac
  echo "=== amendment2 $(date '+%H:%M:%S') starting $C" | tee -a logs/amendment2.log
  scripts/run_logged.sh "$C" 1 main "$AGENT" "$USER_LLM" ${EXTRA[@]+"${EXTRA[@]}"}
  STATUS=$?
  python scripts/check_cell_health.py "results/raw/main__exp_${C}__${AGENT//\//_}/results.json" || { echo "=== amendment2 STOP: $C unhealthy" | tee -a logs/amendment2.log; exit 1; }
  echo "=== amendment2 $(date '+%H:%M:%S') finished $C exit=$STATUS" | tee -a logs/amendment2.log
done
echo "=== amendment2 ALL DONE $(date '+%H:%M:%S')" | tee -a logs/amendment2.log
