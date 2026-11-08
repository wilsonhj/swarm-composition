#!/usr/bin/env bash
# Follow-up runs on the v2 design (exploratory, decided after the frozen v2 run; report separately).
#  1. hinted framing (the middle framing level, implemented but not in the frozen run), both policies,
#     all 8 conditions: Haiku seeds 1000-1019 and Sonnet seeds 1000-1009 (same seeds as the frozen cells).
#  2. More Sonnet seeds for the relay contrast: seeds 1010-1019, both policies x both framings,
#     conditions solo, solo@k5, relay_informed, relay_uninformed (extends Sonnet to 20 distinct seeds there).
# Output: results/v2_followup/. Backend claude-code (subscription), so no OpenRouter spend.
# Analyse with: uv run --no-project python analyze.py results/v2_followup/<prefix>_*.jsonl --md out.md
set -euo pipefail
cd "$(dirname "$0")"

D=${D:-results/v2_followup}; mkdir -p "$D"
DATE=$(date +%Y-%m-%d)
RUN=$(od -An -N4 -tx1 /dev/urandom | tr -d ' \n')
BACKEND=${BACKEND:-claude-code}
BUDGET=()  # claude-code (subscription) has no spend; any other backend must pass an explicit --max-usd
if [ "$BACKEND" != claude-code ]; then
  : "${MAX_USD:?BACKEND=$BACKEND needs MAX_USD set (passed as --max-usd; see CLAUDE.md)}"
  BUDGET=(--max-usd "$MAX_USD")
fi
ALL=solo,solo@k5,solo@k12,pipeline,swarm@n4,swarm_noobj@n4,relay_informed,relay_uninformed
RELAY=solo,solo@k5,relay_informed,relay_uninformed

run() { # model framing seeds offset conds tag
  local model=$1 framing=$2 seeds=$3 offset=$4 conds=$5 tag=$6
  for policy in none strict; do
    local out="$D/${DATE}_${RUN}_${model//\//-}_v2_${policy}_${framing}_${tag}.jsonl"
    echo "=== $(date '+%H:%M:%S') $model policy=$policy framing=$framing seeds=$offset..$((offset + seeds - 1)) -> $out"
    uv run --no-project python harness.py --design v2 --backend "$BACKEND" --model "$model" \
      --policy "$policy" --framing "$framing" --conds "$conds" \
      --seeds "$seeds" --seed-offset "$offset" --out "$out" ${BUDGET[@]+"${BUDGET[@]}"} | tee "${out%.jsonl}.log"
  done
}

echo "run id $RUN"
# 1. hinted framing: <= 2 x 20 x 59 (Haiku) + 2 x 10 x 59 (Sonnet) = 3540 calls
run claude-haiku-5-5 hinted 20 1000 "$ALL" hinted
run claude-sonnet-5-5 hinted 10 1000 "$ALL" hinted
# 2. Sonnet relay seeds 1010-1019: <= 2 policies x 2 framings x 10 x 18 = 720 calls
for framing in neutral explicit; do
  run claude-sonnet-5-5 "$framing" 10 1010 "$RELAY" seeds1010
done
echo "=== $(date '+%H:%M:%S') done (run id $RUN)"
