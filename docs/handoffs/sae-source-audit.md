# Source audit and claim boundaries

Checked **7 November 2026** against primary pages and repository artifacts. This
is a targeted source check, not an independent replication or an exhaustive
literature review. Research rows below use abstracts/metadata except where a
specific full-text section is named. Citation keys resolve in
[references.bib](../research/references.bib). Recheck changing pages before the
final submission; preserve the access date and any changed interpretation.

## Repository facts that affect implementation

| Checked assertion | Evidence | Assessment and implementation consequence |
|---|---|---|
| SAE work can proceed separately from original research | [Main snapshot](https://github.com/wilsonhj/swarm-composition/tree/59c8b7a84e88728d7fb67672dc57d2066bb3aff9), [PR #1 snapshot](https://github.com/wilsonhj/swarm-composition/tree/a5258393ac6baf718b3a2b0042dae195b90f90bd) | Feasible as an engineering/research organization choice. Isolation of code, environment, data and claim status is required; this is a recommendation, not an empirical finding. |
| Existing backend supports sender-only activation steering | [Turns and backend code](https://github.com/wilsonhj/swarm-composition/blob/59c8b7a84e88728d7fb67672dc57d2066bb3aff9/experiments/composition-gap/harness.py) | **False.** Identity is recorded by `Turns`, but only `system,user` are passed to its backend. No local SAE backend is present in the inspected snapshots. |
| Current results are already an SAE experiment | Same code plus [v2 artifact directory](https://github.com/wilsonhj/swarm-composition/tree/59c8b7a84e88728d7fb67672dc57d2066bb3aff9/experiments/composition-gap/results/v2) | **False.** The archived v2 runs use hosted Claude Code inference and a synthetic four-word restriction task. |
| v2 artifact counts and scores can be checked offline | [Pinned input contract](v2-inputs.json), [replay tool](tools/replay_v2.py) | Nine raw files contain 1,040 rows and 7,670 per-turn logical calls, consistent with their manifests; all 1,040 stored legacy score triples reproduce. This is artifact evidence, not future inference determinism. |
| The Sonnet rerun doubles independent task coverage | Original/rerun raw seeds and manifests, retained in replay `audit.json` | **False.** The 80-row rerun reuses the same ten task seeds as its original cell. Original strict/explicit served IDs include both Sonnet 5 and 5.5; rerun reports 5.5. Analyze them separately. |
| `swarm@n8` and `solo@k12` match call opportunity | Harness: three rounds × eight agents versus 12 solo attempts | **False.** Their maximum calls are 24 versus 12. Matching maxima still does not match information sharing, realized calls or token budgets. |
| A proposed provenance protocol is frozen and available on main | [Immutable freeze file](https://github.com/wilsonhj/swarm-composition/blob/435d20d4d0d8e7bf24a391d077649b98e6d526ae/docs/protocols/task-provenance-v1.md) versus main snapshot | Freeze exists in PR #1 history; it is not present on inspected main. Its development results must remain separate from confirmatory collection. |
| The provenance held-out run still needs collection | [Raw artifacts](https://github.com/wilsonhj/swarm-composition/tree/a5258393ac6baf718b3a2b0042dae195b90f90bd/experiments/composition-gap/results/task-provenance), independently rescored offline | **False.** It already contains 800 rows, 50 task seeds, and one failed trial. Five stored score fields reproduce for all 800 rows. Do not repeat inference to recreate its tables. |
| Provenance call denominators are interchangeable | Same raw turns and manifest | **False.** There are 4,795 turn records, including one failed worker turn; the historical backend counter reports 4,794 calls. Preserve both counts and explain the distinction. Do not rewrite the frozen manifest or claim every transport attempt is recoverable. |

The replay pins both raw data and analysis dependencies. Its success is scoped to
that snapshot. Historical attempt-level details cannot be recovered merely by
using a newer analyzer; preserve gaps rather than backfilling invented metadata.
The new SAE track needs more complete events at collection time.

The held-out primary restricted/paraphrase contrast reproduces 45/50 recoverable
under local information versus 0/50 under trusted provenance, a paired −90
percentage-point difference (seed-bootstrap 95% interval −98 to −80; 50 pairs).
Zero observed events is not a guarantee of zero risk: the per-cell Wilson 95%
upper bound is about 7%. Authorized/paraphrase assembly is 15/50 versus 33/49;
the failed provenance trial is excluded from that valid-only denominator and the
paired comparison has 49 pairs. Present sensitivity bounds too. The findings
record a pilot-monitor erratum without changing the frozen protocol hash.

The latest analyzer adds full paired tables and explanatory text to the archived
held-out report; its regenerated Markdown is therefore not byte-identical to the
older report. Existing numeric estimates and intervals reproduce. Record the
analysis revision rather than treating this formatting change as altered raw
data. See [verification commands and limits](verification.md).

## Tooling and artifact compatibility

| Source | What was verified | What remains unverified |
|---|---|---|
| Google DeepMind, [Gemma 3 1B IT card](https://huggingface.co/google/gemma-3-1b-it), `google2025gemma3` | A text-generation instruction-tuned checkpoint exists. Weight access requires acceptance of Gemma terms. | Account access, immutable weight/tokenizer revisions, memory fit, installed-library compatibility and deterministic generation here. |
| Google DeepMind, [Gemma Scope 2 1B IT card](https://huggingface.co/google/gemma-scope-2-1b-it), `google2025gemmascope2` | The suite identifies Gemma 3 1B IT SAEs, including residual-stream artifacts. It gives the release/ID candidate in the implementation contract. | Actual artifact/config identity, hook mapping, normalization and causal usefulness of any chosen feature. The card's example also mentions a conflicting 270M PT model name; resolve using actual config and model identity. |
| [SAELens repository](https://github.com/decoderesearch/SAELens), `saelens2026software` | The former `jbloomAus/SAELens` URL redirects here. The README describes PyTorch-based integration and a v6 migration. | A working pinned dependency combination or loader signature in this project. Copying an older model-card API example is insufficient. |

These checks establish that candidate public artifacts and software exist. They
do not establish that the model has run locally or that the selected SAE/model
pair is validated. In the standard execution environment inspected, the normal
Python environment had no torch/Transformers/SAELens installation and
`nvidia-smi` was unavailable. That does not rule out separately provisioned GPU
access. No weights, paid inference, GPU job or training run was executed for this
handoff. Record base-model terms separately from SAE/software licenses.

## Directly related research

| Source and checked portion | Supported relationship to this project | Claim this project must not infer |
|---|---|---|
| Jones, Dragan & Steinhardt (2024), [Adversaries Can Misuse Combinations of Safe Models](https://arxiv.org/abs/2406.14595), abstract; `jones2024combinations` | Direct precedent for misuse through model combinations and task decomposition. Cite when motivating composition-level evaluation. | Novel discovery that composition alone can defeat every individual model's restrictions; broad harmful capability from the synthetic word task. |
| Shen et al. (2026), [AI Organizations are More Effective but Less Aligned than Individual Agents](https://arxiv.org/abs/2604.10290), abstract/metadata; [companion post](https://alignment.anthropic.com/2026/ai-organizations/); `shen2026aiorgs` | Studies twelve tasks across consultancy/software-team settings and reports a utility/alignment tradeoff for the systems tested. Direct system-level comparison. | The same tradeoff for all models/topologies, or empirical validation of our specific SAE mechanism. |
| Lee & Tiwari (2024), [Prompt Infection: LLM-to-LLM Prompt Injection within Multi-Agent Systems](https://arxiv.org/abs/2410.07283), abstract; `lee2024prompt` | Direct precedent for instructions spreading through inter-agent text. Relevant to message-channel controls and source identity. | Every change in a receiver's answer is infection, covert communication or persistent learning. |
| Wang et al. (2025), [Persona Features Control Emergent Misalignment](https://arxiv.org/abs/2506.19823v2), abstract; `wang2025personafeatures` | SAE/model-diffing evidence for persona-related control in individual models. Motivates testing an interpretable sender intervention. | A transferable feature index for Gemma 3 1B IT, or proof that its messages cause receiver misalignment. |
| Chen et al. (2025), [Persona Vectors: Monitoring and Controlling Character Traits in Language Models](https://arxiv.org/html/2507.21509v3), abstract plus §§2.1–2.2 and Appendix M heading; `chen2025personavectors` | Core vectors are extracted using differences in mean residual activations from contrastive responses; SAE decomposition is a separate analysis. Useful non-SAE comparator and intervention precedent. | Calling every persona vector an SAE feature; attributing this paper's extraction method to an SAE decoder by default. |
| Wu et al. (2025), [AxBench: Steering LLMs? Even Simple Baselines Outperform Sparse Autoencoders](https://arxiv.org/abs/2501.17148v3), abstract; `wu2025axbench` | Compares steering/concept methods on Gemma 2 models and motivates explicit prompting and simple direction baselines. | SAEs will fail on this model/task, or an SAE intervention is superior without controls. |
| Cloud et al. (2025), [Subliminal Learning: Language models transmit behavioral traits via hidden signals in data](https://arxiv.org/abs/2507.14805), abstract; `cloud2025subliminal` | Teacher-generated data can induce traits in students trained on that data in the reported settings. Direct motivation for distinguishing transmission pathways. | Evidence for trait learning in a frozen receiver that only reads a message. |
| Morgulis & Hewitt (2026), [Subliminal Steering: Stronger Encoding of Hidden Signals](https://arxiv.org/abs/2604.25783v2), abstract; `morgulis2026subliminal` | Activation-steered teachers and trained students provide a closer intervention precedent; transfer is reported under full fine-tuning and SGD in that setting. | An inference-only receiver result, or a universal refutation of every LoRA-related finding. |

**Disputed evidence:** Nief et al., [Subliminal Learning is a LoRA Artifact](https://arxiv.org/abs/2606.00831v2)
(`nief2026lora`) has an author warning in arXiv metadata on the access date: “some
of the main claims made in this paper are incorrect.” A substantial revision is
being prepared. Do not use the title as settled negative evidence. The warning
does not identify which individual results remain valid. Retain this warning in
any discussion; it is not evidence that the entire paper is invalid.

These sources establish relevant prior art and design constraints. None directly
establishes the proposed Gemma/SAE sender-to-frozen-receiver effect. Whether that
specific combination has further prior art requires a dedicated novelty review;
the Sunday presentation should avoid priority claims.

## Presentation schedule check

[Organizer page](https://aialignmentfoundation.org/hackathons/swarm-alignment-2026),
`aiaf2026swarm`: Sunday 8 November LA video deadline is 10:00 AM Pacific; selected
live presentations are noon–3:00 PM Pacific. Global report deadline is 23:59 AoE.
The implementation contract's earlier freeze/replay times are internal targets.
