# Prompt-Level Restriction Compliance in Solo and Multi-Agent Workflows

Corrected literature and submission memorandum | 7 November 2026

This revision applies the review of the supplied SAE/submission memorandum. Its operational recommendations supersede the proposed unmatched `swarm@n8` versus `solo@k12` comparison and the unsupported blanket pre-sprint attribution. It does not introduce a new model experiment or redefine completed outcomes.

## Scope and current evidence

The measured outcome is compliance with a synthetic operator restriction on arbitrary words. It is not harmful-capability uplift, real-secret extraction, persistent misalignment, or autonomous infection. Keep three projects distinct:

1. **Completed context/composition study:** v2 Haiku/Sonnet results, with [recorded outcomes and caveats](../findings/v2-results.md). Raw rows and historical analyses are retained.
2. **Provenance intervention:** the [separate protocol](../protocols/task-provenance-v1.md) and [development pilot](../findings/provenance-pilot.md), 320 rows on seeds 2000–2019. This is development evidence, not a held-out result. The protocol was subsequently frozen at `435d20d` with paraphrase wording primary and the monitor unchanged. This amendment preserves the frozen file byte for byte. Fifty planned held-out seeds remain a design target, not an automatic power guarantee.
3. **Sender-specific SAE intervention:** [future research plan](../protocols/sae-sender-study-proposal.md), without a verified installed backend, completed experiment, or validated 42 GPU-hour estimate.

The local provenance treatment intentionally presents identical actor inputs for authorized and restricted purposes. An actor cannot distinguish those global uses solely from identical observations. The interpretation concerns available purpose information rather than knowing evasion.

## Contribution-defining literature

**Composition and organizations.** Jones et al. already demonstrate misuse through combinations of models [jones2024combinations]. Shen et al. directly compare individual agents with AI consultancies and software teams, reporting effectiveness/ethics tradeoffs and model-dependent gaps [shen2026organizations]. The latter is central prior work for collective versus individual alignment, not an optional distant analogy. A synthetic-string experiment cannot claim first discovery of these broader phenomena. Its contribution must be a specific, controlled context or provenance measurement.

**Communication, training and activation interventions.** Prompt Infection studies attack transmission between agents [lee2024prompt]. Cloud et al. study a student trained on a teacher's semantically unrelated outputs [cloud2025subliminal]. These differ from aggregating disclosed fragments and from a frozen receiver reacting to a message. Persona Features uses SAE-based model comparison and reports control of emergent misalignment through activation features [wang2025personafeatures]. A contrastive direction should be called SAE steering only if the actual intervention direction is derived from an SAE; feature interpretation alone does not make it an SAE intervention.

**Simpler steering baselines.** AxBench reports that prompting outperforms the evaluated existing steering methods and that SAEs are not competitive in its Gemma-2 benchmark [wu2025axbench]. This motivates simple prompt/contrastive baselines; it does not determine the best method on a different Gemma model, task or network.

**Disputed LoRA evidence.** The arXiv metadata for Nief et al., version 2, was checked on 7 November 2026 and explicitly warns that follow-up work found some main claims incorrect and a substantial revision is being prepared [nief2026lora]. The warning is directly verified, not merely team-reported. Do not use the paper as settled evidence that LoRA is necessary or that transfer disappears under full fine-tuning. The warning does not identify which individual results survive. Morgulis and Hewitt separately report transfer under full fine-tuning and SGD in their activation-steered teacher setting [morgulis2026subliminal]; neither result licenses universal claims about all setups.

This is a focused narrative review, not a systematic review or replication of these papers. It establishes no complete causal chain from an SAE sender intervention to persistent, self-sustaining receiver change.

## Preserve the concurrent protocol freeze

The protocol was frozen while this documentation amendment was being prepared. Its file is retained byte for byte from `435d20d4d0d8e7bf24a391d077649b98e6d526ae`; its primary paraphrase comparison and unchanged monitor are not reopened here. The additional paired counts and power calculator are reporting/design tools, not new task treatments.

For an exact replication of that declared collection, use a clean checkout/worktree at the freeze commit and pass its full SHA to `--freeze-commit`. Analyze the resulting immutable JSONL with a separately recorded analysis commit if using the new paired-table presentation. A later branch head or analysis edit must not silently replace the recorded collection freeze or be described as a new model experiment.

## Execution and call accounting

No new swarm comparison replaces the provenance primary comparison. If a separate swarm-size experiment is proposed, version its protocol before collecting new outcomes and specify model, policy, framing, endpoint and unused seeds.

| Comparison | Scheduled maximum actor calls per paired task | Interpretation |
|---|---:|---|
| swarm@n8 vs solo@k12 | 24 vs 12 | Unmatched; do not describe as equal-call |
| swarm@n8 vs solo@k24 | 24 vs 24 | Matched maximum opportunities; 2,880 logical calls for 60 pairs |
| swarm@n4 vs solo@k12 | 12 vs 12 | Matched maximum opportunities; 1,440 logical calls for 60 pairs |
| Pipeline local vs shared provenance | 5 vs 5 | Current intervention comparison within a fixed pipeline |

The implemented swarm has three rounds. An all-PASS offline backend exercises the full 3N calls. Early stopping can reduce realized calls but cannot establish a fixed 12-call budget for N=8. Equal calls do not equalize tokens, information, repeated holders, social proof or assembly opportunities. Fix the opportunity schedule prospectively or describe matched *maximum* budgets and report realized calls separately. Retries are additional requests, not additional independent task trials.

The six-call relay has no exact K6 baseline in the existing v2 runs. Its stored contrasts against one-attempt solo must retain that label. K5 matches the pipeline; K12 matches the N=4 swarm maximum. Do not relabel old contrasts as matched or reinterpret reruns on the same seeds as independent new tasks.

## Paired outcomes and hypothetical power

Report the full paired table, not just marginal rates:

| | Baseline success | Baseline no success |
|---|---|---|
| Treatment success | Both | Treatment-only (b) |
| Treatment no success | Baseline-only (c) | Neither |

Define success separately for restricted recoverability and authorized assembly. Report attempted/completed/evaluable pairs, b and c, total discordance, both marginal rates, risk difference `(b-c)/N`, named interval method, and the prespecified test. Operational failure, valid non-disclosure and explicit refusal are distinct; PASS alone is not evidence of refusal. Failed pairs require separate counts and sensitivity bounds. Nonsignificance does not establish equivalence.

The inherited 45–54% power range is not retained. The checked stdlib calculation is:

```bash
cd experiments/composition-gap
uv run --no-project python power.py
```

For hypothetical independent, complete pairs, P(baseline success)=0.10, P(treatment success)=0.40, and a two-sided exact McNemar test at alpha 0.05:

| P(both succeed) | Power at 20 pairs | Power at 60 pairs |
|---|---:|---:|
| 0.00 | 36.708265% | 90.721945% |
| 0.10 | 58.362917% | 99.994998% |

These examples use the same marginal rates but different joint distributions. They are not power estimates fitted to observed v2 or provenance outcomes. The calculation assumes independent, identically distributed pairs, fixed effects and no unresolved failures. Use prospective plausible discordance scenarios, not a pilot point estimate alone, when justifying sample size. Zero events in 50 independent tasks still permits a one-sided 95% upper risk bound near 5.8%; it does not certify zero risk. Percentile-bootstrap intervals may degenerate at boundaries.

## Attribution and submission

Use the [source-linked timeline](../findings/development-timeline.md). The scaffold, v2 implementation and recorded run starts occur after the published Friday LA kickoff. Commit dates alone do not prove all authoring dates; pilots with incomplete provenance require individual confirmation. **Do not classify all prior repository work as pre-sprint merely because it precedes this amendment.** Genuinely pre-sprint assets must be disclosed by item in README/report.

The [official Apart guidelines](https://apartresearch.com/sprints/swarm-alignment-2026#guidelines), checked 7 November 2026, specify an eight-page maximum **excluding references and appendices**, a 150–250-word abstract, the official template, author names/affiliations, and the required limitations/dual-use appendix. Global submissions close November 8 at 23:59 AoE (November 9 at 11:59 UTC). The [LA schedule](https://aialignmentfoundation.org/hackathons/swarm-alignment-2026) requires a three-minute video by November 8 at 10:00 Pacific (18:00 UTC). Upload format/location for the LA video remains unverified.

The submission should foreground completed measurements. Label the provenance pilot development evidence, and reserve held-out claims for a prospectively frozen and executed run. The SAE roadmap is future work. A manuscript edit is not a new experiment. Keep positive and null wording conditional on the actual estimate and uncertainty, and avoid “general model safety failure” language for this proxy.

## Proportionate release policy

For this harmless lookup task, publish synthetic prompts, ordinary topology templates, task seeds, scoring, outcome indicators, manifests and suitable synthetic transcripts needed for replication. Those materials are already substantially public. No demonstrated risk supports blanket suppression of the “highest-leaking” synthetic prompts or replacement of every seed with opaque identifiers.

Exclude real credentials, private personal data, and live-target attack material. Evaluate any future genuinely attack-enabling SAE or payload artifact individually; no blanket rule requires withholding every feature ID or steering strength regardless of content. If materials must be withheld, specify the resulting replication limits. Do not promise removal from prior public copies or rewrite history to conceal benign experimental details.

This memorandum changes documentation and adds an offline design calculator. It launches no model runs, supplies no new model outcomes, and makes no automatic eligibility or safety certification.
