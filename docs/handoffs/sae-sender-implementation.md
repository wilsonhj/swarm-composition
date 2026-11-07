# Claude Code implementation contract: parallel SAE sender study and Sunday audit

**Prepared 7 November 2026. Status: implementation handoff, not a completed experiment.**
The deliverable is an independently runnable SAE sender-intervention feasibility
study alongside an auditable presentation of the existing composition/provenance
research. Prioritize the existing research's audit packet. The SAE track may
produce a validated pilot, a null result, or a documented feasibility failure.
None of those outcomes should delay the original study or change its protocol.

Read repository `CLAUDE.md`, this contract, and the [source audit](sae-source-audit.md).
Citation keys below resolve in [references.bib](../research/references.bib).
The proposed interfaces and paths below are implementation targets. Only the
explicitly labeled **available now** replay command is implemented by this PR.

## 1. Establish the research boundary

The original experiment measures synthetic operator-restriction compliance,
recoverability of four selected words, and assembly of a four-word line. It does
not demonstrate real-world harmful capability or general alignment. The proposed
SAE study asks a different question:

> Does an activation intervention applied only to one sender change an otherwise
> unmodified receiver's measured behavior through the sender's delivered text?

The causal path to test is `sender activation → sender text → receiver output`.
Receiver weights stay frozen. There is no student training. Call a measured
effect **message-mediated behavior change**. Claims of persistent trait transfer,
learning, covert transmission, or a network cascade need additional experiments.
Prompt infection and subliminal learning are related but distinct literatures
(`lee2024prompt`, `cloud2025subliminal`, `morgulis2026subliminal`).

Use the existing repository with a separate branch/worktree, Python environment,
study ID, prompts, protocol, seeds, and results directory. Share frozen task and
scoring code only through explicit pinned dependencies or a documented adapter.
Do not change `experiments/composition-gap/{harness,scoring,analyze}.py`, existing
results/manifests, or frozen provenance prompts/protocols to make SAE integration
convenient. Propose any essential core change separately and rerun its checks.

### Verified repository checkpoints

| Item | Pinned evidence | Consequence |
|---|---|---|
| Main inspected | [`59c8b7a`](https://github.com/wilsonhj/swarm-composition/tree/59c8b7a84e88728d7fb67672dc57d2066bb3aff9) | This handoff starts independently from main. |
| Original provenance implementation | [PR #1](https://github.com/wilsonhj/swarm-composition/pull/1), inspected head [`a525839`](https://github.com/wilsonhj/swarm-composition/tree/a5258393ac6baf718b3a2b0042dae195b90f90bd) | Includes a completed held-out run; unmerged paths must not be presumed available on main. |
| Provenance protocol freeze | [`435d20d`](https://github.com/wilsonhj/swarm-composition/blob/435d20d4d0d8e7bf24a391d077649b98e6d526ae/docs/protocols/task-provenance-v1.md) | Preserve this collection protocol; record later analysis revisions separately. |
| Protocol file SHA256 | `5a8659fea984ee3203f380476e06cdc72829e4b574e88edbbcfbda5800ead978` | Verify before any original confirmatory collection. |
| Separate SAE proposal | [pinned proposal](https://github.com/wilsonhj/swarm-composition/blob/a5258393ac6baf718b3a2b0042dae195b90f90bd/docs/protocols/sae-sender-study-proposal.md) | A proposal, not evidence that local steering runs. |

Do not silently reinterpret a frozen protocol if later advice differs. Document a
deviation and label its analysis exploratory. In particular, original provenance
held-out seeds `3000–3049` belong to that study. Allocate a fresh SAE namespace
(proposed development `10000–10039`, evaluation `11000–11039`), check for collisions,
and record task content as well as seeds. Feature/layer/strength selection must
never use evaluation outputs. Existing model comparisons have different task
counts and a Sonnet served-model exception; see the audit below.

## 2. Milestones and deadlines

Official schedule checked 7 November: the LA **three-minute video** is due Sunday
8 November **10:00 AM Pacific / 18:00 UTC**. Selected teams present **noon–3:00 PM
Pacific**, not Sunday morning. The global report deadline is **23:59 AoE on
8 November / 11:59 UTC on 9 November** (`aiaf2026swarm`). Recheck the organizer
page for changes. The following earlier times are internal targets, not official
deadlines:

| Gate | Completion evidence | Deadline / action if unmet |
|---|---|---|
| G0: contracts and existing-artifact replay | Assigned file owners; pinned contracts; offline v2 replay passes | First work block; original audit runs in parallel with SAE work. |
| G1: local model/SAE compatibility | Actual files, revisions/hashes, correct hook site, successful forward pass, measured memory/latency | Saturday first GPU session. Stop SAE expansion if access/integration remains blocked. |
| G2: sender-only causal control | Routing/cleanup tests; zero/sham checks; reproducible sender effect with utility/coherence check | Saturday, before receiver experiments. A mock pass is insufficient. |
| G3: receiver pilot | Delivered/blocked/replayed messages; unsteered receiver; raw data and uncertainty | Only after G2 and measured runtime fits remaining time. |
| G4: audit and presentation freeze | Clean-checkout replay; complete claim ledger; all figures traceable; SAE labeled by achieved gate | Sunday 09:00 Pacific / 17:00 UTC. |
| G5: cold replay and recording | Independent agent reproduces packet; record at 09:30; upload buffer from 09:45 Pacific | Video due 10:00 Pacific. If SAE evidence fails audit, show its status without an empirical SAE claim. |

Benchmark generation speed and remaining wall-clock budget before choosing the
evaluation sample. Do not assume a GPU allocation, a fixed number of GPU-hours,
or a sufficient sample size. Preserve the original study's resources and review
time. Network size sweeps, judge-model comparisons, fine-tuning, and full circuit
analysis are beyond the Sunday minimum.

## 3. Parallel Claude Code agent assignments

The integrator first commits the call context, manifest, event schema, and protocol
skeleton. Agents then use separate worktrees and commit only owned files. Merge
small reviewed commits in dependency order. Give one agent exclusive ownership of
each shared schema; route requested edits through that owner. On one GPU,
generation is serialized even when implementation work is parallel.

Copy this common instruction into every agent task:

> Read CLAUDE.md and docs/handoffs/sae-sender-implementation.md. Implement only
> your assigned scope. Preserve frozen studies and raw artifacts. Distinguish
> mock, development, held-out, and unavailable evidence. Return a commit, exact
> verification commands, observed results, unresolved assumptions, and an artifact
> inventory with hashes. Do not report empirical results that you did not run.

| Agent | Owned paths / concrete assignment | Required handoff and acceptance |
|---|---|---|
| A: original-study curator | New `tools/audit/` and `artifacts/presentation/` only; read original studies | Extend the available v2 replay to an explicit provenance input allowlist after PR #1 is available. Rescore from accepted per-turn posts, reconcile manifests/failures, separate development from held-out, and build original-study claim rows. Frozen inputs remain byte-identical. |
| B: environment and loader | `experiments/sae-sender/pyproject.toml`, lock, `sae_sender/loader.py`, `environment.md` | Lock an actually tested PyTorch/Transformers/SAELens environment. Verify licensed model access, artifact identity, tensor/site compatibility, activation scaling, and short unsteered generation. Supply G1 evidence and a CPU mock loader for other agents. |
| C: routing and intervention | `sae_sender/context.py`, `intervention.py`, `backend.py`, corresponding tests | Implement explicit sender identity and per-call intervention, scoped hooks, fresh caches, serialized generation, instrumentation events. Pass the negative/control tests in section 5 before any sender-effect claim. Depends on B's hook contract. |
| D: protocol and experimental runner | `docs/protocols/sae-sender-v1.md`, `sae_sender/run.py`, prompts/configs, runner tests | Freeze benign target, selected feature evidence, seed splits, delivery arms, sample/stopping/failure rules. Write append-safe JSONL and atomic manifest finalization; enforce explicit CPU mock versus local model modes. Depends on B/C contracts. |
| E: independent analysis and replay | `sae_sender/analyze.py`, `verify_bundle.py`, analysis tests, new SAE audit artifacts | Implement paired contrasts, full binary tables, uncertainty, failure accounting, manifest validation, and offline replay. Test score tampering and routing leakage; do not select features or tune coefficients on evaluation data. |
| Integrator: presentation and merge | Study README, claim ledger, figure sources, slides/video script, bibliography integration | Review contracts first; merge B/C before real D collection; merge E before reporting. Run a cold audit as a different agent from the collector. Verify every slide claim and keep SAE feasibility distinct from original findings. |

These are work assignments for the Claude Code operator, not evidence that those
agents have already executed. B/C/D can develop against mocks while A/E build the
audit; only G1→G2→G3 have a sequential dependency. If PR #1 merges concurrently,
deduplicate bibliography keys and record the resolved base; do not overwrite its
newer accounting fixes with the older main snapshot.

## 4. Local model and SAE integration contract

Start with **candidate** `google/gemma-3-1b-it` and
`google/gemma-scope-2-1b-it`. The SAE card lists release
`gemma-scope-2-1b-it-resid_post`, example ID `layer_12_width_16k_l0_small`.
These are verified card identifiers, not a verified installation or a scientifically
validated feature. The card has a contradictory model-name example; validate the
downloaded config against the base model. The current SAELens repository has
moved to [`decoderesearch/SAELens`](https://github.com/decoderesearch/SAELens), with
version-dependent interfaces. Do not assume an old tuple return signature works.
See `google2025gemmascope2`, `google2025gemma3`, `saelens2026software`.

Resolve immutable artifact and library revisions. Record SHA256 for actual model
weight shards, tokenizer assets, SAE weights/config, and the direction tensor;
repository names alone are insufficient. Check PT versus IT, model size, layer
index convention, exact module output, `d_in`, decoder orientation, training-time
activation normalization and any inference scaling. A matching tensor shape is
necessary but not sufficient. Do not add quantization until the reference path
has passed; log dtype, device, kernels and attention implementation.

Use a single-process local Transformers/PyTorch path initially. Hosted Claude and
OpenRouter calls in this repository do not expose arbitrary residual-stream hooks.
Keep GPU libraries in the new study's optional environment so original CPU tests
remain lightweight. Model access, terms acceptance, GPU availability, memory fit,
and library compatibility are **unverified** until B records them. No model/GPU
experiment was executed to prepare this handoff.

Select a harmless, independently interpretable feature (for example, a benign
style or preference) using development data and inspection of activating examples.
Record feature index, selection search space, representative positive/negative
examples, selection rule, and utility effects. A Neuronpedia label is a hypothesis,
not causal proof. Do not invent a known "misalignment feature" for this model.

For the initial intervention use an explicitly defined additive decoder
direction, in the model's correct activation units:

```text
d = decoder_direction(feature_index) / L2(decoder_direction(feature_index))
h[b,t,:] = h[b,t,:] + alpha * d    only where the sender and token masks are true
```

Validate nonzero finite norms and feature bounds. Record the original norm and
`alpha` units; never silently normalize twice. Distinguish additive steering,
feature clamping, and SAE reconstruction replacement. Do not replace the residual
with an SAE reconstruction when the protocol specifies adding one direction.
Define whether prefill tokens, the last prompt position, decode tokens, padding,
and cached decoding are intervened on. Log exactly which positions were changed.
Use development-only calibration and freeze strength and token policy before
evaluation. A contrastive mean direction may be a useful comparator
(`chen2025personavectors`); label it as such rather than as an SAE intervention.

## 5. Sender identity, hooks, and meaningful tests

In the current harness, `Turns.__call__(role, agent, part, system, user)` records
identity but invokes `self.llm(system, user)`. That backend cannot know which
agent is speaking. Do not use prompt string matching, global mutable flags, or
the thread's last role to choose a steering target. Build a new explicit interface:

```python
generate(system: str, user: str, *, context: CallContext) -> GenerationResult
# CallContext: study_id, run_id, trial_id, call_id, agent_id, role,
# target_sender_id, condition, intervention_spec_id, task_seed, generation_seed
```

Validate identity and condition before any forward pass. In an intervention arm,
missing or inconsistent target identity is a hard error, never an "all agents"
fallback. Receiver, assembler and monitor calls must carry `intervention=none`.
Register a hook within a context manager, remove it in `finally`, and assert no
unexpected hooks remain. Protect registration, generation, and removal with one
lock when sharing model weights; separate KV caches per call. Do not use the
original harness's multi-threaded worker default with global hooks. Batch support
is optional and requires a verified per-example mask before use.

| Test | Evidence / rejection condition |
|---|---|
| Identity reaches backend | Spy backend observes the exact agent, role and intervention ID for every call. A log entry alone does not pass. |
| Fail before forward | Missing/unknown sender ID, mismatched role or unknown intervention produces no model call and a recorded error. |
| Sender only | Hook event counters/masks show changes only for target sender; receiver, assembler, monitor and non-target senders have zero intervention events. |
| Zero strength | Zero-strength hook versus no hook on identical inputs/RNG matches logits within a predeclared dtype-specific tolerance. |
| No receiver contamination | Fixed receiver input before and after a steered sender call produces matching receiver logits within the same tolerance, including after exceptions/retries. Different delivered messages may legitimately change receiver output. |
| Cleanup | Inject exceptions and exhausted retries; verify hooks removed and the next unrelated call unsteered. |
| Token/site correctness | Small known tensors verify selected tokens/dimensions only; real-model activation probes verify the resolved module/site. A synthetic tensor test alone does not establish G1. |
| Isolation | Concurrent requests are serialized; a later trial cannot inherit cached text, RNG state, intervention settings or generation cache. |
| Perturbation controls | A norm-matched seeded random direction and sham hook use the same site, token policy and generation budget as the SAE arm. |
| Audit failure paths | Truncated JSONL, missing manifest fields, duplicate trial IDs, altered raw text and invalid checksums fail verification; no silent success/default zero. |

Use separate task RNGs and generation RNGs; derive deterministic per-trial seeds
without consuming a shared cross-thread RNG. Tests and mocks establish plumbing.
Only actual local-model outputs establish steering efficacy.

## 6. Minimum experimental design

**Stage 1: sender validation.** Compare no hook, zero-strength hook, chosen SAE
direction, norm-matched random direction, and explicit prompt instruction toward
the same benign target. Use identical development prompts and generation budgets.
If feasible add the contrastive mean comparator. Record target behavior, task
utility, invalid/truncated output, and coherence. Reject a setting that merely
produces a target token by destroying normal generation. Lock target scoring,
feature/layer/strength, utility threshold, and sample plan before held-out use.
AxBench makes prompt and non-SAE controls scientifically necessary
(`wu2025axbench`); a larger SAE is not automatically better steering.

**Stage 2: two-agent receiver test.** One sender and one unsteered receiver, one
fixed message opportunity, a fresh receiver context for each trial. The receiver's
task and benign target adoption score must be written before collection. Exact
marker/style scoring is acceptable for a plumbing pilot, with that limitation;
it is not evidence of a broad personality change. For a semantic trait, freeze a
rubric, blind any judge to assignment, validate against human-scored examples,
and report disagreements. Keep judge calls and costs in the manifest.

Cross the five core sender arms above with delivered versus blocked messages.
The blocked arm uses a fixed neutral placeholder in the same receiver template;
retain both candidate and delivered text. Keep generation caps equal and report
actual tokens, lengths and early stopping. Length/content are possible mediators;
do not erase them by conditioning the primary estimate on post-treatment success
or length. Any content/length-matched secondary analysis needs its own rule.

Replay a recorded message into a fresh receiver and retain its raw input/output.
Verify delivery order, source identity and message hashes. This tests the text
channel and excludes accidental direct receiver steering. A blocked-message
control need not be exactly zero in finite stochastic samples; report its effect
and uncertainty. Receiver invariance on **identical** inputs is the implementation
test in section 5. An observed sender effect without receiver change is a useful
negative pilot outcome. Expand beyond two agents only after this path is audited.

**Primary estimand:** the paired difference in receiver target-adoption rate
between SAE and no-hook sender arms when messages are delivered. Report the
blocked-arm contrast and the delivered-minus-blocked difference as prespecified
channel checks; prompt/random/zero comparisons are secondary unless preregistered
otherwise. Sender target adoption is the manipulation check. Include receiver
task utility and sender/receiver failure rates alongside target adoption.

Proposed initial evaluation target: 40 distinct held-out task/prompt IDs, each
with one preregistered generation seed per condition. Five arms × two delivery
settings × 40 tasks = 400 trials and, for two generations per trial, 800 model
calls before retries or optional comparators. This is a planning count, not a
power calculation or runtime promise. B benchmarks; D/E freeze the affordable
sample and minimum detectable effect/precision before evaluation. A smaller run
is labeled an underpowered pilot. Do not stop at the first favorable p-value.

For each binary comparison publish all four paired outcomes `(0,0),(0,1),(1,0),
(1,1)`, the distinct task count, paired effect, 95% interval and exact two-sided
McNemar test if used. Resample whole task clusters for bootstrap intervals,
preserving all arm/delivery/repeated-generation records within a cluster. Specify
bootstrap iterations and RNG. Use a single primary contrast and mark unadjusted
secondary tests exploratory, or declare multiplicity correction in advance.
For failures report total/valid/failed/unknown, complete-pair analysis, and binary
worst/best-case sensitivity; do not silently discard failed arms. Multiple random
directions or receiver samples within one task are not independent task seeds.

## 7. Append-only raw data and complete manifests

Use new `experiments/sae-sender/results/<study_id>/<run_id>/`. Refuse overwrite;
resume only through explicit recovery that checks config hashes and unique trial
keys. Write structured attempt events before classifying an exhausted call, flush
completed trials, then atomically finalize manifest status. Partial/interrupted
runs remain visible and must never be marked complete. Preserve parse failures.

Minimum trial record:

```text
schema_version, study_id, run_id, trial_id, task_id, task_seed, generation_seed,
condition, delivery_mode, sender_id, receiver_id, protocol_hash, config_hash,
sender_call_id, receiver_call_id, sender_raw, candidate_message, delivered_message,
message_sha256, receiver_input, receiver_raw, parsed_scores,
validity_status, errors, call_ids, elapsed_ms
```

Minimum call/attempt event:

```text
call_id, attempt_id, role, agent_id, requested_model, served_model_or_revision,
intervention_spec_id, actual_hook_site, actual_token_mask, hook_event_count,
prompt_hash, input/output tokens, finish_reason, latency, error,
reported_cost_or_null, generation_seed
```

Copy [the manifest template](templates/sae-run-manifest.template.json); implement a
validator with stage-specific required fields. Every artifact file record needs
path, size and SHA256. Reject `status=template`, missing revisions, unresolved
required nulls, empty evaluation splits, duplicate IDs, and missing raw files.
Explicit unavailable metadata needs a reason; missing cost is not `$0`. Record
logical calls separately from generation/transport attempts. Never write secrets
or `.env` into the packet. Keep nonredistributable weights out of Git; publish
checksums and access instructions sufficient to fetch the exact licensed assets.

## 8. Reproduce, explain, and audit

Three different promises must be separated:

1. **Artifact replay:** clean checkout plus archived raw data regenerates scores,
   tables, figures, and claim ledger offline. This must pass for every Sunday
   empirical claim.
2. **Fresh inference repeatability:** pinned local weights/SAE/environment and RNG
   can rerun inference within measured numerical tolerances. GPU determinism must
   be tested; hosted model IDs do not guarantee identical future generations.
3. **Scientific replication:** new tasks, seeds, hardware or models test external
   validity. Neither replay nor a single toy-model pilot establishes this.

### Available now: existing v2 replay

From a checkout of this handoff PR's exact commit, with Python 3.11:

```bash
python3 docs/handoffs/tools/replay_v2.py --out /tmp/swarm-v2-replay
cd /tmp/swarm-v2-replay
sha256sum -c SHA256SUMS
```

The output directory must be new and outside the source checkout. The script
checks 21 pinned files (nine raw files, nine manifests, three analysis sources),
reconciles **1,040 rows / 7,670 logged logical calls**, and reproduces all stored
legacy score triples. It writes separate `haiku.md`, `sonnet_original.md`, and
`sonnet_rerun.md`, `audit.json`, and `SHA256SUMS`. It captures per-run collection
commits, actual analysis-checkout commit, Python/platform, and reported served IDs.
It uses the existing deterministic analyzer and does not overwrite archived tables.
This validates the artifact snapshot, not fresh inference or every historical
transport attempt. A dirty-checkout flag is recorded; presentation evidence must
come from a clean checkout. If future source/data changes fail pinned hashes,
check out the handoff commit; do not just bless new hashes to make the check pass.

Haiku contributes 640 rows over 20 task seeds per cell; original Sonnet 320 over
10; the Sonnet strict/explicit rerun adds 80 rows on the **same ten tasks**. The
original Sonnet strict/explicit manifest lists both `claude-sonnet-5` and
`claude-sonnet-5-5`; retain this fact and analyze the rerun separately. Overall row
count is not an independent sample size. Maximum call opportunity also differs:
three-round `swarm@n8` allows 24 calls while `solo@k12` allows 12. Match opportunity
explicitly or present that contrast with its limitation; log realized calls too.

### Implementation targets: provenance and SAE replay

Agent A must add the original provenance replay using an explicit input allowlist
and collection/analysis commits. Read the immutable protocol before selecting
its metric. PR #1 now contains [held-out artifacts and findings](https://github.com/wilsonhj/swarm-composition/blob/a5258393ac6baf718b3a2b0042dae195b90f90bd/docs/findings/provenance-heldout.md),
separate from its development pilot. Audit those existing artifacts first; do not
repeat collection merely to recreate a table. Preserve the reported failure and
the findings' pilot-monitor erratum; leave the frozen protocol text/hash intact.
Any additional confirmatory collection remains a separate decision/run.

The audited held-out snapshot has 800 rows / 50 task seeds and one failed trial.
It logs 4,795 turns including the failure, while its historical backend counter
reports 4,794 calls. Preserve both quantities in the packet; do not silently
equate completed/accounted calls with every logical turn or retry. The
[verification note](verification.md) gives a working offline analysis command.

Agents D/E must provide these **proposed**, not currently executable, interfaces:

```text
python -m sae_sender.run --config CONFIG --backend mock --out NEW_RUN_DIR
python -m sae_sender.run --config FROZEN_CONFIG --backend local --out NEW_RUN_DIR
python -m sae_sender.analyze --manifest MANIFEST --out NEW_ANALYSIS_DIR
python -m sae_sender.verify_bundle --bundle BUNDLE_DIR --offline
```

Document the actually implemented commands, including dependency installation
from the lockfile and GPU test invocation. `verify_bundle` must recompute scores
from raw text, reconcile attempted/completed/failed denominators, verify hashes,
rebuild every table/figure/claim, and exit nonzero for missing evidence or invalid
claims. It must not contact a model or generate substitute examples. Run it with
network access disabled and credentials absent after collection.

Publish this packet, with a small README mapping every file to a command:

- Collection and analysis commit IDs, clean-tree status, frozen protocol/prompt
  hashes, exact environment lock, seeds, model/SAE revisions and artifact hashes.
- Raw trials and attempt logs, run manifests, scored rows, complete denominators,
  paired tables, uncertainty settings, generated figures and machine-readable values.
- [Claim ledger](templates/claim-ledger.template.csv): slide/claim → study/status →
  row selection and hashes → estimate/uncertainty → primary citations → limitation.
- A deterministic replay entry point, expected output hashes for its pinned
  environment, independent replay log, and any deviations/negative findings.

Explain a result by walking one representative trial through its task, operator
instruction, candidate/accepted message, scorer decision and causal comparison.
Show both an ordinary and a failure/counterexample trace under a stated selection
rule. Do not select only favorable anecdotes. An SAE feature label or compelling
model-written explanation does not establish the mechanism: the controlled
intervention, routing checks and channel controls provide that evidence.

## 9. Sunday acceptance and presentation script

Release only when the independent reviewer can answer **yes** to all applicable
checks: raw-to-table replay passes offline; original frozen files are unchanged;
development versus held-out status is visible; all failures and unique task counts
are included; served-model exceptions are disclosed; every empirical slide claim
has a ledger row and uncertainty; directly related work is cited by checked title
and source; no template/mock output is presented as real-model evidence.

Do not display rounded `p=0.000` as a literally zero probability; use the exact
value or `p < 0.001` as appropriate. Do not turn `0/50` observed disclosures into
a claim of guaranteed prevention; report its interval and tested scope.

For an empirical SAE slide also require G1/G2 and the relevant G3 controls to
pass, actual local output artifacts to exist, and sender/receiver utility and
failure metrics to be shown. If only G1 or CPU mocks work, report that exact
engineering status. If steering or transfer is absent, report the null pilot and
its precision. Never relabel completion pressure as evidence.

Suggested three-minute video: 25 seconds for the synthetic restriction question
and why composition matters (`jones2024combinations`, `shen2026aiorgs`);
35 seconds for the experimental unit and controls; 60 seconds for audited original
results and uncertainty; 30 seconds for the achieved SAE gate and its limits;
30 seconds for reproducibility command, related-work boundaries and takeaway.
Use only values regenerated into the final claim ledger. Link the exact artifact
commit and source audit on the last slide. Preserve pre-existing versus weekend
work attribution as required by `CLAUDE.md`; preparation of this handoff is not
independent replication of the cited research.
