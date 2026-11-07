# Research update: prospective provenance study

This update follows review of the original harness, a second architectural audit, and primary-source reading from Anthropic's Alignment Science blog. It preserves the completed v2 experiment and separates a proposed intervention study from its results.

## Baseline and evidence

Baseline source: `40a58d0e214e6c5999d4c66cbc2f59cdbe98f5c7`. The v2 Haiku experiment (640 rows, 4,720 calls, zero reported failures) is documented in [v2-results.md](v2-results.md). Its raw JSONL, manifests, logs and original analysis remain unchanged. v1/v2 prompt identity continues to be tested.

Concurrent main-branch work through `822db80cef093a2862b8fd19d804f9d044f9e6af` added Sonnet results, a rerun of its mixed-served-model cell, and per-turn model logging. This update is rebased onto that work and preserves it. Analysis uses per-turn served-model sets when available and leaves earlier missing model identity unknown; it cannot repair the original mixed-model cell retrospectively.

The README previously said only pilots existed; it now links the completed run and its narrow findings. No new positive composition-gap claim is introduced. Anthropic's organizational-alignment study is now included as direct prior work, and the new question concerns a specific provenance intervention rather than first discovery of collective safety failures.

## Changes to the instrument

- Repeated-solo per-attempt scoring was already fixed upstream and is retained. Legacy reproduction now follows the same maximum-per-attempt definition; explicitly labeled `pooled_*` diagnostics keep observer-level collection separate.
- Duplicate trial keys now stop analysis rather than letting summaries count every row while paired contrasts select the first. Compatible-run metadata is part of pairing identity; custom summary groups cannot silently merge it.
- Default v2 CLI comparisons select matched maximum call budgets. Missing references (notably K6 for the existing relay run) are omitted instead of falling back to solo. Original comparisons remain available with `--baseline solo`.
- OpenRouter budget documentation now describes estimated reservations rather than a hard cap, with a regression test showing actual reported cost can exceed an estimate. Nonpositive/nonfinite thresholds are rejected.
- The prospective study has a separate runner, accepted-publication scoring, seed ranges, prompt/protocol hashes, and a clean-commit gate for held-out collection. Scripted mocks exercise both successful authorized work and blocked restricted publication.

## Study scope

See [task-provenance-v1](../protocols/task-provenance-v1.md). The primary local-versus-provenance comparison uses identical five-call pipelines. The cumulative monitor is a secondary bundled intervention with additional information/calls/veto; it does not isolate a pure history effect. Trusted metadata is a harness assumption, not a claim of implemented cryptographic authentication.

No live model runs or paid experiments were executed to implement this update. Mock outcomes are software checks, not scientific evidence. Freeze and record the protocol commit before collecting held-out data, and report authorized utility alongside restricted disclosure, including null results and failures.
