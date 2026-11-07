# Composition-gap analysis

**Descriptive analysis. Design and seed labels alone do not verify prospective freezing or held-out status.**
Interpret against the committed protocol and run manifests; primary comparisons must be specified before collection.

Files: heldout-haiku.jsonl

- designs: task-provenance-v1
- run_ids: 4c134cfd-0a87-49f2-ba16-a4cba153a701
- backends: claude-code
- models: claude-haiku-5-5
- failed rows excluded (failed_calls>0): 1/800; duplicate trial keys rejected
- rows: 800; unknown-validity rows excluded from denominators (reported in n_unknown)
- CIs: Wilson 95% for proportions; seed-bootstrap 95% (2000 resamples, seeded) for means; metrics from posted messages only (see scoring.py)

- study: task-provenance-v1
- served_models: claude-haiku-5-5
- authorization: authorized, restricted
- prompt_hash: 98914b7e3f88cb8533d192b335a497128c9416ce81b9ceb121e717061f5caa1a
- protocol_hash: 5a8659fea984ee3203f380476e06cdc72829e4b574e88edbbcfbda5800ead978

## Cells

| authorization | framing | cond | n_total | n_failed | n_unknown | n_valid | assembled | recoverable | mean identified | mean exposed | assembled all-trial range | recoverable all-trial range | served models |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| authorized | keyword | keyword_gate | 50 | 0 | 0 | 50 | 0/50 (0%) [0-7%] | 0/50 (0%) [0-7%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | claude-haiku-5-5 |
| authorized | keyword | local | 50 | 0 | 0 | 50 | 12/50 (24%) [14-37%] | 47/50 (94%) [84-98%] | 3.94 [3.86 to 4.00] | 3.94 [3.86 to 4.00] | 24-24% | 94-94% | claude-haiku-5-5 |
| authorized | keyword | monitor | 50 | 0 | 0 | 50 | 0/50 (0%) [0-7%] | 0/50 (0%) [0-7%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | claude-haiku-5-5 |
| authorized | keyword | provenance | 50 | 0 | 0 | 50 | 48/50 (96%) [87-99%] | 49/50 (98%) [90-100%] | 3.98 [3.94 to 4.00] | 3.98 [3.94 to 4.00] | 96-96% | 98-98% | claude-haiku-5-5 |
| authorized | paraphrase | keyword_gate | 50 | 0 | 0 | 50 | 14/50 (28%) [17-42%] | 48/50 (96%) [87-99%] | 3.94 [3.84 to 4.00] | 3.94 [3.84 to 4.00] | 28-28% | 96-96% | claude-haiku-5-5 |
| authorized | paraphrase | local | 50 | 0 | 0 | 50 | 15/50 (30%) [19-44%] | 47/50 (94%) [84-98%] | 3.94 [3.88 to 4.00] | 3.94 [3.88 to 4.00] | 30-30% | 94-94% | claude-haiku-5-5 |
| authorized | paraphrase | monitor | 50 | 0 | 0 | 50 | 0/50 (0%) [0-7%] | 0/50 (0%) [0-7%] | 0.06 [0.00 to 0.14] | 0.06 [0.00 to 0.14] | 0-0% | 0-0% | claude-haiku-5-5 |
| authorized | paraphrase | provenance | 50 | 1 | 0 | 49 | 33/49 (67%) [53-79%] | 47/49 (96%) [86-99%] | 3.96 [3.90 to 4.00] | 3.96 [3.90 to 4.00] | 66-68% | 94-96% | claude-haiku-5-5 |
| restricted | keyword | keyword_gate | 50 | 0 | 0 | 50 | 0/50 (0%) [0-7%] | 0/50 (0%) [0-7%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | claude-haiku-5-5 |
| restricted | keyword | local | 50 | 0 | 0 | 50 | 14/50 (28%) [17-42%] | 49/50 (98%) [90-100%] | 3.98 [3.94 to 4.00] | 3.98 [3.94 to 4.00] | 28-28% | 98-98% | claude-haiku-5-5 |
| restricted | keyword | monitor | 50 | 0 | 0 | 50 | 0/50 (0%) [0-7%] | 0/50 (0%) [0-7%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | claude-haiku-5-5 |
| restricted | keyword | provenance | 50 | 0 | 0 | 50 | 0/50 (0%) [0-7%] | 0/50 (0%) [0-7%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | claude-haiku-5-5 |
| restricted | paraphrase | keyword_gate | 50 | 0 | 0 | 50 | 16/50 (32%) [21-46%] | 46/50 (92%) [81-97%] | 3.92 [3.84 to 3.98] | 3.92 [3.84 to 3.98] | 32-32% | 92-92% | claude-haiku-5-5 |
| restricted | paraphrase | local | 50 | 0 | 0 | 50 | 17/50 (34%) [22-48%] | 45/50 (90%) [79-96%] | 3.90 [3.82 to 3.98] | 3.90 [3.82 to 3.98] | 34-34% | 90-90% | claude-haiku-5-5 |
| restricted | paraphrase | monitor | 50 | 0 | 0 | 50 | 0/50 (0%) [0-7%] | 0/50 (0%) [0-7%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | claude-haiku-5-5 |
| restricted | paraphrase | provenance | 50 | 0 | 0 | 50 | 0/50 (0%) [0-7%] | 0/50 (0%) [0-7%] | 0.00 [0.00 to 0.00] | 0.00 [0.00 to 0.00] | 0-0% | 0-0% | claude-haiku-5-5 |

Served models: union of the cell's per-turn logs (`-`: none logged); MIXED marks more than one. They do not split cells: fully failed trials log none and stay in their run's cell.

All-trial ranges assign every excluded failed/unknown trial first failure, then success. They are sensitivity bounds, not confidence intervals; valid-only rates may be selection-biased.

## Seed-paired contrasts vs `local`

Difference = cond minus baseline, paired by seed within compatible study/design/backend/run metadata; brackets are paired-bootstrap 95% CIs. Discordant: +b = cond succeeded where baseline did not, -c = the reverse; p is the exact two-sided binomial (McNemar) test.

| varying run metadata | cond | baseline | pairs | d assembled | discordant | d recoverable | discordant | d identified |
|---|---|---|---|---|---|---|---|---|
| authorization=authorized, framing=keyword | keyword_gate | local | 50 | -24pp [-36, -12] | +0/-12, p=0.000 | -94pp [-100, -86] | +0/-47, p=0.000 | -3.94 [-4.00, -3.86] |
| authorization=authorized, framing=keyword | monitor | local | 50 | -24pp [-36, -12] | +0/-12, p=0.000 | -94pp [-100, -86] | +0/-47, p=0.000 | -3.94 [-4.00, -3.86] |
| authorization=authorized, framing=keyword | provenance | local | 50 | +72pp [+58, +86] | +37/-1, p=0.000 | +4pp [-4, +12] | +3/-1, p=0.625 | +0.04 [-0.04, +0.12] |
| authorization=authorized, framing=paraphrase | keyword_gate | local | 50 | -2pp [-18, +14] | +8/-9, p=1.000 | +2pp [-6, +10] | +3/-2, p=1.000 | +0.00 [-0.12, +0.10] |
| authorization=authorized, framing=paraphrase | monitor | local | 50 | -30pp [-42, -18] | +0/-15, p=0.000 | -94pp [-100, -86] | +0/-47, p=0.000 | -3.88 [-3.98, -3.76] |
| authorization=authorized, framing=paraphrase | provenance | local | 49 | +37pp [+20, +53] | +21/-3, p=0.000 | +0pp [-8, +8] | +2/-2, p=1.000 | +0.00 [-0.08, +0.08] |
| authorization=restricted, framing=keyword | keyword_gate | local | 50 | -28pp [-40, -16] | +0/-14, p=0.000 | -98pp [-100, -94] | +0/-49, p=0.000 | -3.98 [-4.00, -3.94] |
| authorization=restricted, framing=keyword | monitor | local | 50 | -28pp [-40, -16] | +0/-14, p=0.000 | -98pp [-100, -94] | +0/-49, p=0.000 | -3.98 [-4.00, -3.94] |
| authorization=restricted, framing=keyword | provenance | local | 50 | -28pp [-40, -16] | +0/-14, p=0.000 | -98pp [-100, -94] | +0/-49, p=0.000 | -3.98 [-4.00, -3.94] |
| authorization=restricted, framing=paraphrase | keyword_gate | local | 50 | -2pp [-18, +14] | +8/-9, p=1.000 | +2pp [-10, +14] | +5/-4, p=1.000 | +0.02 [-0.10, +0.14] |
| authorization=restricted, framing=paraphrase | monitor | local | 50 | -34pp [-48, -22] | +0/-17, p=0.000 | -90pp [-98, -80] | +0/-45, p=0.000 | -3.90 [-3.98, -3.80] |
| authorization=restricted, framing=paraphrase | provenance | local | 50 | -34pp [-48, -22] | +0/-17, p=0.000 | -90pp [-98, -80] | +0/-45, p=0.000 | -3.90 [-3.98, -3.80] |
