# Paper review and evidence check

Reviewed November 7, 2026. Scientific evidence is unchanged from the frozen repository records. GPT-6 Astra reviewed the framing as an academic advisor; two GPT-6.1 Terra assistants audited the studies separately. Their findings were integrated and checked by the coordinating agent. No new model experiments were run.

## Were both studies completed and validated?

Both studies completed their planned collection schedules. Their recorded results reproduce offline. Neither study establishes a general mechanism of rule following or a safeguard that works across models, tasks and untrusted metadata.

| Check | Study 1 | Study 2 |
|---|---|---|
| Collected records | 640 Haiku rows, 320 Sonnet rows, 80 Sonnet rerun rows | All 800 planned keys: 16 cells × 50 seeds |
| Valid records | 1,040; no recorded failures | 799; one backend failure excluded without replacement, as required |
| Call accounting | 7,670 logged calls | 4,795 logged turns; manifest counts 4,794 completed calls and one error |
| Offline verification | All three historical analyses reproduced byte-for-byte | All 800 rows rebuilt and rescored; 16 cells and four main paired contrasts reproduced |
| Main inferential limit | Small samples, bundled framing cues, no six-call solo baseline; relay comparison is inconclusive | One model, one pipeline, fixed wordings and trusted metadata |
| Replication limit | Sonnet rerun reuses the same seeds; original strict/explicit cell has mixed served models | No second-model or cross-provider replication |

Study 1's collection plan and findings are in [run_v2.sh](../../experiments/composition-gap/run_v2.sh) and [v2 results](../../docs/findings/v2-results.md). Study 2's design, exclusions and required outcomes are in the [frozen protocol](../../docs/protocols/task-provenance-v1.md); its [held-out findings](../../docs/findings/provenance-heldout.md) and [replay documentation](../../docs/handoffs/verification.md) explain provenance and accounting limits. A committed freeze and recorded start time do not independently establish preregistration or prove that nobody inspected held-out seeds beforehand.

The Study 2 primary result remains restricted recoverability of 45/50 with local context versus 0/50 with provenance: −90 percentage points, paired-bootstrap 95% CI [−98, −80], exact McNemar p < 0.001. Authorized assembly is 15/50 versus 33/49; the paired effect is +37 points [20, 53] on 49 valid pairs. Subtracting those two marginal percentages is not the paired calculation.

## Corrections in this edition

- The abstract and introduction distinguish the shared organizing hypothesis from Study 1's diagnostic comparison and Study 2's intervention test. The hypothesis is not retroactively described as preregistered.
- The discussion emphasizes recoverability across posts and authorized completion. Low assembly alone can reflect coordination failure.
- A Sonnet denominator is corrected: 10 main-run explicit-solo trials plus 10 rerun trials, rather than 20 main-run trials. An unmatched 17/20-to-7/30 policy comparison was removed from the discussion.
- The keyword result is narrowed to the tested gate. Two fixed wording pairs do not exclude other lexical heuristics or establish general semantic reasoning.
- The appendix now reports the four protocol-specified monitor-versus-keyword-gate contrasts. Small exact p-values are shown as `p < 0.001`, not rounded to `p=0.000`.
- Additional secondary outcomes are explicitly accounted for: on every frozen Study 2 row, exact-string assembly equals normalized assembly, and exposed-part counts equal identified-part counts. Thus their cell and paired statistics coincide in this dataset; the definitions remain different.
- The paper corrects the maximum role count, removes an unsupported counterfactual “lower bound” claim, and clarifies that the swarm implements early stopping but no recorded run triggered it.
- The related-work monitor claim is scoped to the cited [adversarial evaluation](https://alignment.anthropic.com/2026/red-teaming-auto-mode/). The [METR incident](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) remains motivation, not evidence for this experiment's mechanism. These primary sources were rechecked; the entire bibliography was not re-audited externally in this pass.

Original run files, collection code and frozen protocols remain unchanged. The editorial patch changes the manuscript and appendix presentation, including these corrections, while preserving the empirical evidence. The compact edition keeps key tables and all original figures in the paper; exhaustive tables and exact prompts/transcripts are preserved in linked repository supplements.

## Verification and reproduction

The preceding academic fact-check passed: 250 harness tests with the Anthropic SDK installed, nine claim-checker regression tests, eight handoff tests, documentation validation, and the claim ledger with zero integrity problems. The ledger retains explicitly classified historical and not-recomputable entries; passing it does not mean every literature claim was independently proved.

The [secondary calculation](secondary-metrics.py) uses the established scorer, 2,000-resample seeded bootstrap and exact McNemar routine. [Its output](secondary-metrics.txt) records the endpoint equivalences and all eight monitor-versus-baseline secondary contrasts. From the repository root:

```sh
python3 report/submission/secondary-metrics.py
python3 experiments/composition-gap/analyze.py \
  experiments/composition-gap/results/task-provenance/heldout-haiku.jsonl \
  --baseline keyword_gate --md /tmp/provenance-keyword-contrasts.md
```

## Compact edition and data-quality checks

The PDF and Word document contain the same **20-page edition**, down from 43 pages: main text 1–8, references 9–10, Appendix A 11–12, Appendix B 13–16 and Appendix C 17–20. Two new methods diagrams show the distinct study designs and the recorded seed-3000 input/output sequence. The four original figures remain unchanged. Full prompts, cell tables and transcripts are preserved in the [extended methods/results supplement](supplements/extended-methods-and-results.md), with the [extended limitations](supplements/extended-limitations.md) also retained. Paper links pin those supplements to commit `c41b43a2dd476ea78cfade54df46e28ac238cb0a`.

The [data-quality check](data-quality/check.py) freshly verified frozen source/manifest/protocol hashes, unique trial keys, expected grid coverage, valid denominators, served-model metadata coverage, reported cells and the seed-3000 inputs and responses. [Its results](data-quality/results.json) confirm 1,040 valid Study 1 records and 800 Study 2 records, 799 valid. Original Study 1 turns lack per-turn served-model IDs except the rerun; the one failed Study 2 turn has no model ID. No missing outcome was imputed. These checks support the descriptive figures, not prospective or external validity.

```sh
python3 report/submission/data-quality/check.py > /tmp/swarm-paper-data-quality.json
cmp report/submission/data-quality/results.json /tmp/swarm-paper-data-quality.json
```

Final artifact checks covered the full author name, 196-word abstract, all 29 unchanged references, all 85 compact Appendix B table-cell strings, all original main-table rows, 89 prose lines, six figures, template parts, embedded fonts and page margins. All 136 exact prompt/transcript lines are preserved in the linked supplement. All 20 pages were visually reviewed; the corrected table page was reviewed again and the other final page images matched the reviewed render byte-for-byte. The [manifest](manifest.json) records file and source hashes.

Further scientific work remains: independent model/provider replication, more relay seeds with a six-call solo baseline, varied wording, forged-metadata tests, and larger asynchronous systems. The SAE intervention remains unimplemented. Software tests and replay do not replace these experiments.
