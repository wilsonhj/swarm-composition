#!/usr/bin/env bash
# Frozen full run (design-freeze tag). Haiku: 20 seeds x 3 framings; Sonnet: 10 seeds, neutral framing.
# Relay conditions don't use framing, so they run once (neutral). Rows with failed_calls>0 are excluded in analysis.
set -euo pipefail
cd "$(dirname "$0")"
D=results/full; mkdir -p "$D"; TAG=2026-11-06
run() { # model framing seeds conds
  local out="$D/${TAG}_$1_strict_$2.jsonl"
  echo "=== $(date '+%H:%M:%S') $1 $2 seeds=$3 -> $out"
  uv run --no-project python harness.py --backend claude-code --model "$1" --policy strict \
    --framing "$2" --seeds "$3" --conds "$4" --out "$out" | tee "${out%.jsonl}.log"
}
ALL=solo,pipeline,swarm,swarm_noobj,relay,relay_uninformed
CORE=solo,pipeline,swarm,swarm_noobj
run claude-haiku-5-5 neutral 20 "$ALL"
run claude-haiku-5-5 hinted 20 "$CORE"
run claude-haiku-5-5 explicit 20 "$CORE"
run claude-sonnet-5-5 neutral 10 "$ALL"
echo "=== $(date '+%H:%M:%S') done"
