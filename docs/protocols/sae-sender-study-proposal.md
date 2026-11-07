# Sender-specific activation intervention: future study proposal

**Status:** unimplemented proposal, outside the completed v2 study and the provenance intervention. No local SteeredLocal/Gemma backend was found in the reviewed repository snapshot (`a2e6a7b` on main; `9de815c` on the provenance branch). A “sender-routing bug” in separate unpublished code needs a repository/commit reference before diagnosis. No 42 GPU-hour budget or exact Gemma 3 IT/Gemma Scope 2 integration is validated here.

## Scientific question

Does an intervention applied only to a designated sender change an untreated receiver's behavior through the sender's messages? This is a causal message-transmission question. Durable trait learning and autonomous multi-hop propagation are later, distinct hypotheses.

## Engineering prerequisites

1. Verify the exact model checkpoint, instruction-tuning variant, SAE checkpoint, layer, hook location, normalization, dtype and inference implementation. Measure memory/throughput on a small local smoke run before budgeting GPU hours.
2. Carry a stable agent identity and explicit intervention assignment on every inference path. Missing or ambiguous assignments must prevent an intervention trial from running, rather than steering every agent by default.
3. Scope hooks to the designated sender; isolate batched examples, KV caches, retries and assembler calls. Test that untreated receivers are numerically unchanged on identical inputs when the sender hook is idle or absent.
4. Establish a sender behavior change while measuring coherence and legitimate task performance. A corrupted, incoherent sender is not a clean behavioral manipulation.

## Controls before network claims

- No intervention, a strength-matched sham/random direction, and a simpler prompt or contrastive-vector comparator as appropriate. AxBench motivates these baselines [wu2025axbench], not their guaranteed superiority in this setting.
- Message replay to untreated receivers, blocked-message arms, and fixed recipient inputs. These distinguish sender-output changes from recipient routing or environment artifacts.
- Fresh-agent and clean-context tests, with external memory explicitly retained or cleared. Persistence while the original cue remains in context is different from persistence after cue removal.
- Separate receiver behavior, later transmission to another fresh receiver, multi-hop continuation without renewed attacker cues, and persistence. None follows automatically from collective disclosure.

Predefine benign target behaviors and endpoints before feature/strength selection. Keep development and evaluation tasks distinct. Do not label a contrastive activation direction “SAE steering” unless the intervened direction actually comes from an SAE. A receiver reacting to changed text is not evidence that the same internal SAE feature or weights transferred to that receiver [wang2025personafeatures, cloud2025subliminal, morgulis2026subliminal].

Publish the harmless replication details unless an artifact-specific review identifies a concrete disclosure concern. This is not a rule to hide every feature ID, seed or steering strength. Follow the [submission memo's release policy](../research/revised-sae-review-and-submission-memo.md#proportionate-release-policy).

No feature search, model download, training, GPU job or network propagation experiment is launched by this proposal.
