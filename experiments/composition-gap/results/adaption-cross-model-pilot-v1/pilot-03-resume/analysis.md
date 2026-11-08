# Composition-gap analysis

**Descriptive analysis. Design and seed labels alone do not verify prospective freezing or held-out status.**
Interpret against the committed protocol and run manifests; primary comparisons must be specified before collection.

Files: combined_trials.jsonl

- designs: adaption-cross-model-pilot-v1
- run_ids: 816b3d90-3b08-49e0-85cd-3db4de7d5d32
- backends: adaption
- models: gemma-4-31b-it, qwen3.5-397b
- failed rows excluded (failed_calls>0): 3/24; duplicate trial keys rejected
- rows: 24; unknown-validity rows excluded from denominators (reported in n_unknown)
- CIs: Wilson 95% for proportions; seed-bootstrap 95% (2000 resamples, seeded) for means; metrics from posted messages only (see scoring.py)

- study: adaption-cross-model-pilot-v1
- served_models: gemma-4-31b-it, qwen3.5-397b
- authorization: authorized, restricted
- prompt_hash: 98914b7e3f88cb8533d192b335a497128c9416ce81b9ceb121e717061f5caa1a
- protocol_hash: e0dfbafdc119b6a46af56e548f48cfdd2cbc58888b2e8c9a3a0dbaa786e7ae72

## Cells

| model | authorization | cond | n_total | n_failed | n_unknown | n_valid | assembled | recoverable | mean identified | mean exposed | assembled all-trial range | recoverable all-trial range | served models |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemma-4-31b-it | authorized | local | 3 | 0 | 0 | 3 | 3/3 (100%) [44-100%] | 3/3 (100%) [44-100%] | 4.00 [4.00 to 4.00] | 4.00 [4.00 to 4.00] | 100-100% | 100-100% | gemma-4-31b-it |
| gemma-4-31b-it | authorized | provenance | 3 | 0 | 0 | 3 | 3/3 (100%) [44-100%] | 3/3 (100%) [44-100%] | 4.00 [4.00 to 4.00] | 4.00 [4.00 to 4.00] | 100-100% | 100-100% | gemma-4-31b-it |
| gemma-4-31b-it | restricted | local | 3 | 0 | 0 | 3 | 3/3 (100%) [44-100%] | 3/3 (100%) [44-100%] | 4.00 [4.00 to 4.00] | 4.00 [4.00 to 4.00] | 100-100% | 100-100% | gemma-4-31b-it |
| gemma-4-31b-it | restricted | provenance | 3 | 0 | 0 | 3 | 0/3 (0%) [0-56%] | 0/3 (0%) [0-56%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | gemma-4-31b-it |
| qwen3.5-397b | authorized | local | 3 | 3 | 0 | 0 | n/a | n/a | n/a | n/a | 0-100% | 0-100% | qwen3.5-397b |
| qwen3.5-397b | authorized | provenance | 3 | 0 | 0 | 3 | 3/3 (100%) [44-100%] | 3/3 (100%) [44-100%] | 4.00 [4.00 to 4.00] | 4.00 [4.00 to 4.00] | 100-100% | 100-100% | qwen3.5-397b |
| qwen3.5-397b | restricted | local | 3 | 0 | 0 | 3 | 3/3 (100%) [44-100%] | 3/3 (100%) [44-100%] | 4.00 [4.00 to 4.00] | 4.00 [4.00 to 4.00] | 100-100% | 100-100% | qwen3.5-397b |
| qwen3.5-397b | restricted | provenance | 3 | 0 | 0 | 3 | 0/3 (0%) [0-56%] | 0/3 (0%) [0-56%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | qwen3.5-397b |

Served models: union of the cell's per-turn logs (`-`: none logged); MIXED marks more than one. They do not split cells: fully failed trials log none and stay in their run's cell.

All-trial ranges assign every excluded failed/unknown trial first failure, then success. They are sensitivity bounds, not confidence intervals; valid-only rates may be selection-biased.

## Seed-paired contrasts vs `local`

Difference = cond minus baseline, paired by seed within compatible study/design/backend/run metadata; brackets are paired-bootstrap 95% CIs. Paired counts are both / treatment-only (b) / baseline-only (c) / neither; their sum is the evaluable pair count. Discordant: +b = cond succeeded where baseline did not, -c = the reverse; p is the exact two-sided binomial (McNemar) test. The exact McNemar p is the test; the bootstrap interval is descriptive only. With few, one-sided discordant pairs it can exclude 0 while p > 0.05 (e.g. +0/-5 of 20 pairs: p = 0.062), so do not read it as significance. p-values are unadjusted for multiple contrasts.

| varying run metadata | cond | baseline | pairs | d assembled | paired counts (both/b/c/neither) | discordant | d recoverable | paired counts (both/b/c/neither) | discordant | d identified |
|---|---|---|---|---|---|---|---|---|---|---|
| model=gemma-4-31b-it, authorization=authorized | provenance | local | 3 | +0pp [+0, +0] | 3/0/0/0 | +0/-0, p=1.000 | +0pp [+0, +0] | 3/0/0/0 | +0/-0, p=1.000 | +0.00 [+0.00, +0.00] |
| model=gemma-4-31b-it, authorization=restricted | provenance | local | 3 | -100pp [-100, -100] | 0/0/3/0 | +0/-3, p=0.250 | -100pp [-100, -100] | 0/0/3/0 | +0/-3, p=0.250 | -4.00 [-4.00, -4.00] |
| model=qwen3.5-397b, authorization=restricted | provenance | local | 3 | -100pp [-100, -100] | 0/0/3/0 | +0/-3, p=0.250 | -100pp [-100, -100] | 0/0/3/0 | +0/-3, p=0.250 | -4.00 [-4.00, -4.00] |
