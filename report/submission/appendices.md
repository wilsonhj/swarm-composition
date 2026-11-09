# Appendix A: Limitations and Dual-Use / Ethical Considerations

## A.1 Measurement and interpretation

The studies test a synthetic rule on harmless strings, not trained-in refusal or a transferable jailbreak. Only accepted posts count. Exposed parts count target mentions; identified parts exclude other items from the same list in that post. Recoverability requires four identified parts or assembly. Warnings quoting targets can count; distractors, encodings, inflections and reordered words can evade scoring. Sonnet strict/neutral swarm seed 1004 illustrates undercounting.

Low scores can also reflect task failure. In the no-policy pipeline and relay worker diagnostic, 36/695 posts omit the target (pipeline 4/240; informed relay 10/226; uninformed relay 22/229). This includes non-lookup posts and excludes swarm and strict-policy turns. No-policy neutral swarms never assemble the phrase.

## A.2 Design and inference

Study 1 has 10-20 seeds per cell and roughly seven unadjusted comparisons. Framing changes multiple cues together. Hinted framing and swarms above four agents occur only in exploratory work, outside the confirmatory design. Relay framing cells and the verified-model rerun repeat tasks. Their pooled trial counts are not independent seed counts. Equal call caps do not equalize tokens or information; the six-call relay lacks an exact solo control. Fixed roles and turns exclude asynchronous or tool-using coordination.

Study 2 uses one model and two fixed wording pairs. Local inputs cannot distinguish authorization; supplied purpose is trusted, not authenticated. Forgery and tampering are untested. There are no purpose-only or length-matched context controls, and the paraphrase does not exclude other lexical cues. The monitor changes information, calls and veto power together; no stateless ablation or prompt-tuning comparison isolates them. It yields no authorized completions. A committed protocol freeze is not independent preregistration or proof that seeds were never inspected.

Shared prompts, vocabulary and services limit independence assumptions. Bootstrap intervals can disagree with exact tests. Zero in fifty permits about 5.8% failure at a one-sided 95% bound under independent Bernoulli trials, with no guarantee under distribution shift.

## A.3 Dual-use ethics and research assistance

These findings could help someone hide a restricted objective behind ordinary local tasks or distribute disclosure across posts to evade checks on complete answers. The public harness uses harmless strings, with no harmful-task decompositions or live-target attack material; transfer to harmful tasks remains untested.

No human subjects, personal data, live credentials or harmful payloads were used. Public inputs and transcripts support auditing. A future transferable vendor weakness would require a disclosure assessment. No pre-sprint assets were used (C.5). The [extended limitations](https://github.com/wilsonhj/swarm-composition/blob/c41b43a2dd476ea78cfade54df46e28ac238cb0a/report/submission/supplements/extended-limitations.md) retain the longer discussion.

**LLM Usage Statement.** Claude and Codex assisted coding, review and report preparation. Numerical results were checked against frozen artifacts by independent outcome scoring and offline replay; a separate claim ledger covers earlier source documents. The author is responsible for the submission.

# Appendix B: Study 1 Methods and Supporting Results

## B.1 Conditions and information

![Four Study 1 topologies: solo, pipeline, swarm and relay](../figures/fig1_topologies.png)

*Figure B1. Solo sees all lists. Pipeline workers see one list each; the assembler sees their board. Swarm agents share a board in fixed round-robin order. The relay coordinator sees no lists. All roles receive the same policy.*

| Condition | Actors | Maximum calls | Task information |
|---|---|---|---|
| solo | one | 1 | all four lists |
| solo@k5 / solo@k12 | one | 5 / 12 | all lists; best single attempt |
| pipeline | 4 + 1 | 5 | one list per worker; board for assembler |
| swarm@n4 | four | 12 | own list, board, team objective |
| swarm_noobj@n4 | four | 12 | own list and board; no team objective |
| relay informed / uninformed | 1 + 4 | 6 | coordinator: board; worker: own list, position, board |

Every list has six disjoint vocabulary items; positions are seed-determined. The strict policy forbids passphrase disclosure, including individual words; the no-policy prompt omits that rule. Neutral framing requests inventory lookups; explicit framing identifies passphrase parts. The [full methods supplement](https://github.com/wilsonhj/swarm-composition/blob/c41b43a2dd476ea78cfade54df46e28ac238cb0a/report/submission/supplements/extended-methods-and-results.md) preserves exact prompts. All 260 swarm runs use twelve calls, with no early stops.

<!-- PAGE BREAK -->

## B.2 All Study 1 outcome cells

![Study 1 assembly and recoverability by model, policy, framing and condition](../figures/fig2_v2_heatmap.png)

*Figure B2. Frozen v2 held-out results. Cells show successes/valid trials; assembly is left, recoverability right. Sonnet includes the same-seed verified-model rerun. The dagger marks an original cell listing two served models. Relay prompts ignore framing, so those columns repeat the same task instructions rather than distinct framing interventions.*

<!-- PAGE BREAK -->

## B.3 Relay comparisons and model provenance

| Strict policy, pooled framing | Haiku informed | Haiku uninformed | Sonnet informed | Sonnet uninformed |
|---|---|---|---|---|
| Coordinator sent a request | 0/40 | 7/40 | 0/30 | 27/30 |
| Assembled | 0/40 | 1/40 | 0/30 | 7/30 |
| Recoverable | 0/40 | 3/40 | 0/30 | 13/30 |
| No-policy assembly | 29/40 | 16/40 | 9/20 | 17/20 |

*Table B1. Sonnet strict totals combine twenty original trials and ten rerun trials on the same ten seeds. Seven assemblies come from four seeds; thirteen recoverable trials from seven. One pooled cell has mixed served models. Excluding it gives 5/20 assembled and 9/20 recoverable.*

Against informed solo, the uninformed Sonnet main-run relay differs by +20 pp assembled (95% CI [0, +50], exact p = 0.50) and +40 pp recoverable ([+10, +70], p = 0.125). Rerun differences are +10 pp ([0, +30]) and +20 pp ([0, +50]). Solo/explicit is 0/10 in both runs. Haiku differences are +5 pp assembled ([0, +15]) and +15 pp recoverable ([0, +30]). These small-sample comparisons do not establish a decomposition effect.

Against equally uninformed solo, relay assembly is lower: Sonnet strict/neutral 4/10 versus 8/10, and Haiku 1/40 pooled relay trials versus 19/20 solo trials. Informed coordinators under strict policy send no requests (0/70); without the policy all do (40/40 Haiku, 20/20 Sonnet). Of 27 strict-policy uninformed Sonnet requests, 22 mention the passphrase, usually as a warning. Such warnings do not identify the lookup items as its words.

**Models and calls.** Claude Code runs used claude -p without tools and provider-default sampling. Haiku 5.5 has twenty seeds and 4,720 calls; original Sonnet 5.5 has ten seeds and 2,360 calls. The Sonnet strict/explicit manifest lists claude-sonnet-5 and claude-sonnet-5-5 without per-turn attribution. A 590-call rerun on the same seeds logs claude-sonnet-5-5 for every turn. It assembles the uninformed relay in 1/10 trials and makes it recoverable in 2/10, versus 2/10 and 4/10 in the original corresponding cell. Totals are 1,040 valid rows and 7,670 logged calls, with no recorded failures.

**Exploratory work.** The Haiku strict/neutral batch from the stopped exploratory v1 full run (seeds 0-19) assembles solo in 20/20 and pipeline/swarms in 0/20, with recoverability in 12-20 of twenty. It is excluded from v2 inference.

A separate Sonnet extension used seeds 1010-1019 for solo, five-attempt solo and both relays (160 trials, 720 calls). Under the strict rule, uninformed relays assembled in 4/10 explicit and 2/10 neutral trials, versus 0/10 and 8/10 for solo. All four manifests mark the working tree dirty; two explicit-cell turns list both Sonnet 5 and 5.5. These exploratory results are excluded from confirmatory analyses. The [follow-up report](https://github.com/wilsonhj/swarm-composition/blob/c363e3b118932b1e20a19949a971fe41dbc0fabf/docs/findings/v2-followup.md) gives model sensitivities and additional hinted-framing exploration. Neither supplies cross-provider replication.

# Appendix C: Study 2 Evidence and Reproduction

## C.1 Fixed pipeline and publication controls

![Study 2 pipeline and its four information and control conditions](../figures/fig5_provenance_design.png)

*Figure C1. Workers do not read one another's replies. The assembler receives accepted posts. Provenance adds trusted original purpose to every actor. The LLM monitor sees objective, sender, accepted board and proposal, but no target, seed, lists, selected positions or scores. The keyword gate inspects the objective. Blocked proposals are not published.*

The same lookups are paired with authorized inventory and restricted passphrase objectives. Local worker prompts and assembler instructions do not vary by authorization; sampled replies can differ. In provenance, the system prompt supplies the original objective plus a contribution statement. The paraphrase objective avoids the gate's policy keywords; the authorized keyword objective explicitly states that the items are not passphrase material. This tests two fixed wording pairs, not arbitrary paraphrases. Exact strings are preserved in the [full supplement](https://github.com/wilsonhj/swarm-composition/blob/c41b43a2dd476ea78cfade54df46e28ac238cb0a/report/submission/supplements/extended-methods-and-results.md).

<!-- PAGE BREAK -->

## C.2 Worked input and recorded responses

![Seed 3000 inputs, agent replies, accepted boards and scored outcomes](figures/seed3000-workflow.png)

*Figure C2. A recorded restricted/paraphrase trial pair, not an aggregate estimate. Local workers post their selected words; with trusted purpose all five actors return PASS. Each lane makes five actor calls. Recoverability permits reconstruction across posts; assembly requires one post joining the four words in order.*

| Worker | Six-word list in order | Position | Selected word |
|---|---|---|---|
| 0 | umber, ember, jade, cobalt, iris, zephyr | 2 | ember |
| 1 | xenon, yarrow, onyx, tundra, harbor, willow | 6 | willow |
| 2 | violet, koi, dune, lotus, nectar, fjord | 4 | lotus |
| 3 | garnet, maple, raven, sage, quartz, birch | 4 | sage |

*Table C1. Seed-3000 inputs. Each worker receives only its own row. The restricted paraphrase asks for four secret words opening the company strongroom; authorized objectives request an inventory report. Supplement B.3.4 preserves [stored raw replies and reconstructed inputs](https://github.com/wilsonhj/swarm-composition/blob/c41b43a2dd476ea78cfade54df46e28ac238cb0a/report/submission/supplements/extended-methods-and-results.md).*

<!-- PAGE BREAK -->

## C.3 All sixteen held-out cells

| Condition | Paraphrase restricted | Paraphrase authorized | Keyword restricted | Keyword authorized |
|---|---|---|---|---|
| local | 45/50 / 17/50 | 47/50 / 15/50 | 49/50 / 14/50 | 47/50 / 12/50 |
| provenance | 0/50 / 0/50 | 47/49 / 33/49 | 0/50 / 0/50 | 49/50 / 48/50 |
| monitor | 0/50 / 0/50 | 0/50 / 0/50 | 0/50 / 0/50 | 0/50 / 0/50 |
| keyword gate | 46/50 / 16/50 | 48/50 / 14/50 | 0/50 / 0/50 | 0/50 / 0/50 |

*Table C2. Each cell gives recoverable / assembled, using valid n. Restricted recoverability is the safety endpoint; authorized assembly is the utility endpoint. One authorized/paraphrase/provenance backend failure is excluded; all restricted cells have fifty valid trials.*

![Study 2 restricted recoverability and authorized assembly with Wilson intervals](../figures/fig4_provenance_heldout.png)

*Figure C3. Haiku 5.5 held-out seeds 3000-3049. Lower restricted recoverability is better (left); higher authorized assembly is better (right). Bars include Wilson 95% intervals. The asterisk marks the cell with one excluded backend failure. Zero restricted disclosure with no authorized completion does not establish a useful safeguard.*

On every recorded row, exact-string assembly equals normalized assembly, and exposed-part counts equal identified-part counts. The definitions differ even though these outcomes coincide here. The [secondary calculation script](https://github.com/wilsonhj/swarm-composition/blob/7d1d0b7db028da46a33b3a8d3fb40b3aba6f41a1/report/submission/secondary-metrics.py) reproduces these checks.

<!-- PAGE BREAK -->

## C.4 Paired contrasts and collection disclosures

| Provenance minus local | Wording | Change in pp [95% CI] | Discordant + / - | Exact p |
|---|---|---|---|---|
| Primary restricted recoverability | paraphrase | -90 [-98, -80] | 0 / 45 | < 0.001 |
| Authorized assembly | paraphrase | +37 [+20, +53] | 21 / 3 | < 0.001 |
| Restricted recoverability | keyword | -98 [-100, -94] | 0 / 49 | < 0.001 |
| Authorized assembly | keyword | +72 [+58, +86] | 37 / 1 | < 0.001 |

*Table C3. Seed-paired differences with 2,000 paired-bootstrap resamples. Authorized paraphrase uses 49 complete pairs: local 15/49 and provenance 33/49. The excluded seed 3010 was a local non-completion, giving the all-valid local rate 15/50 in Table C2. All other contrasts use fifty pairs. Only the first row is primary.*

| Monitor minus keyword gate | Assembled pp [95% CI]; discordance; p | Recoverable pp [95% CI]; discordance; p |
|---|---|---|
| Authorized keyword | 0 [0, 0]; +0/-0; 1.000 | 0 [0, 0]; +0/-0; 1.000 |
| Authorized paraphrase | -28 [-40, -16]; +0/-14; < 0.001 | -96 [-100, -90]; +0/-48; < 0.001 |
| Restricted keyword | 0 [0, 0]; +0/-0; 1.000 | 0 [0, 0]; +0/-0; 1.000 |
| Restricted paraphrase | -32 [-46, -20]; +0/-16; < 0.001 | -92 [-98, -84]; +0/-46; < 0.001 |

*Table C4. Secondary, unadjusted comparisons within fifty complete seed pairs per row. Both conditions can block publication; the LLM monitor additionally evaluates proposals and accepted history. Full local-baseline and identified-part contrasts remain in the supplement.*

**Failure.** A worker backend error at seed 3010 in authorized/paraphrase/provenance leaves 49 valid trials. All-trial bounds are 66-68% assembled and 94-96% recoverable. There are no malformed monitor verdicts or non-protocol replies.

**Call accounting.** There are 4,795 logged turns: 4,000 actor and 795 monitor, including one failed turn without a model ID. The manifest's backend counter records 4,794 completed calls. Every logged served-model ID is claude-haiku-5-5. Manifest-reported cost is $0.96, billed to a subscription; these records do not establish an independently audited bill or all transport retries.

**Pilot erratum.** The frozen protocol says the pilot monitor blocked every authorized proposal. It blocked 160/161 authorized proposals (320/321 overall), allowing one keyword-authorized proposal at seed 2018. The protocol remains unedited to preserve its hash; the decision to keep that monitor unchanged does not depend on the error.

<!-- PAGE BREAK -->

## C.5 Evidence access and independent checks

**Protocol and sampling.** The separate Study 2 protocol was frozen at 435d20d4d0d8e7bf24a391d077649b98e6d526ae before recorded held-out collection. Development seeds 2000-2019 informed the primary paraphrase comparison; held-out seeds are 3000-3049. Pilot results are not pooled. Study 1's v2 design followed pilots on 0-19 and uses held-out Haiku seeds 1000-1019 and Sonnet 1000-1009. Git chronology and manifests document the workflow without independently authenticating every collection event.

**Archived evidence.** [Study 1 frozen runs](https://github.com/wilsonhj/swarm-composition/tree/7d1d0b7db028da46a33b3a8d3fb40b3aba6f41a1/experiments/composition-gap/results/v2) and [Study 2 held-out records](https://github.com/wilsonhj/swarm-composition/tree/7d1d0b7db028da46a33b3a8d3fb40b3aba6f41a1/experiments/composition-gap/results/task-provenance) contain raw replies, manifests and analyses. The [full methods and results supplement](https://github.com/wilsonhj/swarm-composition/blob/c41b43a2dd476ea78cfade54df46e28ac238cb0a/report/submission/supplements/extended-methods-and-results.md) preserves exact prompt templates, exhaustive tables and transcripts. These commit-pinned links identify the reviewed evidence edition.

**Offline audit.** The [verification guide](https://github.com/wilsonhj/swarm-composition/blob/7d1d0b7db028da46a33b3a8d3fb40b3aba6f41a1/docs/handoffs/verification.md) gives pinned inputs and commands. Replay verifies archived hashes, reconstructs trials from logged replies, and recomputes scores and tables without model calls or an LLM judge. It checks the recorded evidence, not whether future inference reproduces the behavior. Fresh model runs test replication; additional tasks, models, providers and forged-metadata tests assess generalization.

**Data quality.** The [scoped check script](https://github.com/wilsonhj/swarm-composition/blob/c41b43a2dd476ea78cfade54df46e28ac238cb0a/report/submission/data-quality/check.py) and [recorded results](https://github.com/wilsonhj/swarm-composition/blob/c41b43a2dd476ea78cfade54df46e28ac238cb0a/report/submission/data-quality/results.json) check hashes, unique trial keys, grid coverage, validity and seed-3000 inputs/outputs. Study 1 has 1,040 valid records; Study 2 has all 800 planned keys and 799 valid records. Original Study 1 turns lack per-call model IDs except in the rerun. Successful Study 2 turns have IDs; its failed turn does not. Failed outcomes are not imputed and runs are not silently pooled.

**Sprint provenance.** The author confirms that all study assets were produced during the sprint. Public history records the scaffold at 17:24 and v2 implementation at 18:29 Pacific on November 6, after the 13:30 LA kickoff; the first v2 manifest records 18:49. Study 2 collection ran 06:01-06:57 UTC on November 7. The [source-linked development timeline](https://github.com/wilsonhj/swarm-composition/blob/7d1d0b7db028da46a33b3a8d3fb40b3aba6f41a1/docs/findings/development-timeline.md) records these timestamps. Eleven pilot result files in the initial scaffold lack execution timestamps, so the records do not independently date every asset. No assets are claimed as pre-sprint work.

Independent replication, varied objectives, adversarial purpose metadata and larger asynchronous networks remain future work. The proposed sender-level SAE intervention is unimplemented. Completed collection and replay establish internal reproducibility within the stated provenance limits, not independent behavioral replication.
