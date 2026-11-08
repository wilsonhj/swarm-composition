# Exploratory Adaption cross-model pilot: completed 24 assignments

This is a separate exploratory follow-up, not a revision of either frozen study.
Seeds 5000–5002, Gemma 4 31B and Qwen 3.5 397B, paraphrase wording,
local/provenance × restricted/authorized: 24 assignments, 21 valid and three failed.

The [canonical combined dataset](../../experiments/composition-gap/results/adaption-cross-model-pilot-v1/pilot-03-resume/combined_trials.jsonl)
has one row per assigned trial and explicit source lineage; use it alone.
The [analysis](../../experiments/composition-gap/results/adaption-cross-model-pilot-v1/pilot-03-resume/analysis.md)
retains the frozen scorer's failure exclusions and pairs within model.

| Model | Restricted recoverable, local → provenance | Authorized assembled, local → provenance |
|---|---|---|
| Gemma 4 31B | 3/3 → 0/3 | 3/3 → 3/3 |
| Qwen 3.5 397B | 3/3 → 0/3 | N/A (3 failed) → 3/3 |

Three seeds per cell are insufficient for a general safety or replication claim;
the exact paired restricted-task p-value is 0.25 for each model. Qwen's three
authorized/local trials exhausted the 4,096-token generation allowance and are
excluded, so its authorized utility contrast cannot be estimated. No valid trial
had a nonprotocol reply. Do not interpret generation failures as scored refusals.

The original pilot-01 and partial pilot-02 files remain intact. The continuation
preserved five valid source trials and replayed two successful partial-trial calls.
All 27 successful source calls were reused without new POSTs. The old 504 was
retried once; its unknown charge remains reserved. Terminal incomplete generations
were retained as failed outcomes instead of resampled.

Across all attempts: 117 actual POSTs; reported 15,710 input and 75,013 output
tokens (74,379 reasoning tokens within output). Usage for the original 504 is
unknown. Known configured-rate estimates total 0.26656538 credits plus a retained
0.015711-credit reservation: 0.28227638 accounted against a two-credit estimated
limit. Peak accounted usage was 0.29376953. Account balance/invoice was not verified.
OpenRouter was not used.

See the [summary](../../experiments/composition-gap/results/adaption-cross-model-pilot-v1/pilot-03-resume/summary.json)
and [resume guide](../dev/adaption-resume.md). The source/frozen protocols, harness,
scorer, analyzer, original results and submission report remain unchanged.
