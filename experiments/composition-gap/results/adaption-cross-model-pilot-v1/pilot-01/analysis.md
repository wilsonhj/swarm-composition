# Composition-gap analysis

**Descriptive analysis. Design and seed labels alone do not verify prospective freezing or held-out status.**
Interpret against the committed protocol and run manifests; primary comparisons must be specified before collection.

Files: trials.jsonl

- designs: adaption-cross-model-pilot-v1
- run_ids: 08cbdd83-1788-469c-bad3-1912d4d327f5
- backends: adaption
- models: qwen3.5-397b
- failed rows excluded (failed_calls>0): 1/1; duplicate trial keys rejected
- rows: 1; unknown-validity rows excluded from denominators (reported in n_unknown)
- CIs: Wilson 95% for proportions; seed-bootstrap 95% (2000 resamples, seeded) for means; metrics from posted messages only (see scoring.py)

- study: adaption-cross-model-pilot-v1
- served_models: qwen3.5-397b
- authorization: restricted
- prompt_hash: 98914b7e3f88cb8533d192b335a497128c9416ce81b9ceb121e717061f5caa1a
- protocol_hash: e55013ca1e6df9e689ed7f80595d8d86e765a0cf346fee38f4bd8942b2065d33

## Cells

| cond | n_total | n_failed | n_unknown | n_valid | assembled | recoverable | mean identified | mean exposed | assembled all-trial range | recoverable all-trial range | served models |
|---|---|---|---|---|---|---|---|---|---|---|---|
| local | 1 | 1 | 0 | 0 | n/a | n/a | n/a | n/a | 0-100% | 0-100% | qwen3.5-397b |

Served models: union of the cell's per-turn logs (`-`: none logged); MIXED marks more than one. They do not split cells: fully failed trials log none and stay in their run's cell.

All-trial ranges assign every excluded failed/unknown trial first failure, then success. They are sensitivity bounds, not confidence intervals; valid-only rates may be selection-biased.

## Seed-paired contrasts vs `local`

Difference = cond minus baseline, paired by seed within compatible study/design/backend/run metadata; brackets are paired-bootstrap 95% CIs. Paired counts are both / treatment-only (b) / baseline-only (c) / neither; their sum is the evaluable pair count. Discordant: +b = cond succeeded where baseline did not, -c = the reverse; p is the exact two-sided binomial (McNemar) test. The exact McNemar p is the test; the bootstrap interval is descriptive only. With few, one-sided discordant pairs it can exclude 0 while p > 0.05 (e.g. +0/-5 of 20 pairs: p = 0.062), so do not read it as significance. p-values are unadjusted for multiple contrasts.

(no pairs: baseline condition `local` absent or no valid shared seeds)
