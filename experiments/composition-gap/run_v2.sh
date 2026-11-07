#!/usr/bin/env bash
# Confirmatory v2 run. Held-out seeds 1000-1019 (pilots used 0-19).
# Crossed factors: policy {none, strict} x framing {neutral, explicit}; every condition runs in every cell.
# Each harness call writes <out>.jsonl + <out>.jsonl.manifest.json; output names are unique (date + short id),
# and harness.py refuses to overwrite an existing file. Rows with failed_calls>0 are excluded in analysis.
# Analyse afterwards with: uv run --no-project python analyze.py results/v2/<prefix>_*.jsonl --md out.md
set -euo pipefail
cd "$(dirname "$0")"

D=results/v2; mkdir -p "$D"
DATE=$(date +%Y-%m-%d)
RUN=$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')   # short id shared by every file of this invocation
SEEDS=${SEEDS:-20}
MODEL=${MODEL:-claude-haiku-5-5}   # e.g. MODEL=claude-sonnet-5-5 SEEDS=10 ./run_v2.sh
OFFSET=1000
POLICIES="none strict"
FRAMINGS="neutral explicit"
CONDS=solo,solo@k5,solo@k12,pipeline,swarm@n4,swarm_noobj@n4,relay_informed,relay_uninformed
# Max backend calls per seed, by condition (swarm stops early once the joined secret is posted):
# solo 1 + solo@k5 5 + solo@k12 12 + pipeline 5 + swarm@n4 12 + swarm_noobj@n4 12 + relay 6 + relay 6
PER_SEED=59

cells() { echo $(( $(wc -w <<<"$POLICIES") * $(wc -w <<<"$FRAMINGS") )); }

run() { # backend model seeds [extra harness args...]
  local backend=$1 model=$2 seeds=$3; shift 3
  for policy in $POLICIES; do
    for framing in $FRAMINGS; do
      local out="$D/${DATE}_${RUN}_${model//\//-}_v2_${policy}_${framing}.jsonl"
      echo "=== $(date '+%H:%M:%S') $backend $model policy=$policy framing=$framing seeds=$OFFSET..$((OFFSET + seeds - 1)) -> $out"
      uv run --no-project python harness.py --design v2 --backend "$backend" --model "$model" \
        --policy "$policy" --framing "$framing" --conds "$CONDS" \
        --seeds "$seeds" --seed-offset "$OFFSET" --out "$out" "$@" | tee "${out%.jsonl}.log"
    done
  done
}

echo "run id $RUN: $(cells) cells x $SEEDS seeds x <= $PER_SEED calls = <= $(( $(cells) * SEEDS * PER_SEED )) calls ($MODEL)"
run claude-code "$MODEL" "$SEEDS"

# Optional: Sonnet replication, 10 seeds (<= 4 cells x 10 x 59 = 2360 calls). Uncomment to run.
# echo "Sonnet: <= $(( $(cells) * 10 * PER_SEED )) calls"
# run claude-code claude-sonnet-5-5 10

# Optional: OpenRouter cross-model check. Spend comes from the fixed $250 credit: run `make credits` first.
# --max-usd is a hard cap per harness call (one cell), so total spend <= cells x MAX_USD.
# OR_MODEL=vendor/model; MAX_USD=5
# echo "OpenRouter $OR_MODEL: <= $(( $(cells) * SEEDS * PER_SEED )) calls, <= \$$(( $(cells) * MAX_USD ))"
# run openrouter "$OR_MODEL" "$SEEDS" --max-usd "$MAX_USD"

echo "=== $(date '+%H:%M:%S') done (run id $RUN)"
