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

Original run files, collection code and frozen protocols remain unchanged. The editorial patch changes the manuscript and appendix presentation, including these corrections, while retaining all original empirical table values, exact prompts, transcripts, references and figures.

## Verification and reproduction

Fresh local checks passed: 250 harness tests with the Anthropic SDK installed, nine claim-checker regression tests, eight handoff tests, documentation validation, and the claim ledger with zero integrity problems. The ledger retains explicitly classified historical and not-recomputable entries; passing it does not mean every literature claim was independently proved.

The [secondary calculation](secondary-metrics.py) uses the established scorer, 2,000-resample seeded bootstrap and exact McNemar routine. [Its output](secondary-metrics.txt) records the endpoint equivalences and all eight monitor-versus-baseline secondary contrasts. From the repository root:

```sh
python3 report/submission/secondary-metrics.py
python3 experiments/composition-gap/analyze.py \
  experiments/composition-gap/results/task-provenance/heldout-haiku.jsonl \
  --baseline keyword_gate --md /tmp/provenance-keyword-contrasts.md
```

The PDF and Word document have identical editorial content. Verification checked the full author name, 196-word abstract, all 29 references, 1,567 appendix table-cell strings, 136 exact prompt/transcript lines, four figures, source prose, template parts, embedded fonts and page margins. All 43 pages were visually reviewed; the main paper is eight pages. The [manifest](manifest.json) records the final checksums and source hashes.

Further scientific work remains: independent model/provider replication, more relay seeds with a six-call solo baseline, varied wording, forged-metadata tests, and larger asynchronous systems. The SAE intervention remains unimplemented. Software tests and replay do not replace these experiments.
