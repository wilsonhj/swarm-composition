# Critical scientific and editorial review

Reviewed November 8, 2026. This assessment covers the current submission manuscript and appendices, the repository evidence at `c363e3b118932b1e20a19949a971fe41dbc0fabf`, and selected primary research sources. It is an editorial assessment, not external peer review or a prediction of acceptance.

## Final correction pass

The subsequent review corrections are applied in the submission PDF and Word document. Appendix B.3 now discloses the separately reported Sonnet extension, including dirty-tree and mixed-model qualifications, without pooling it into confirmatory results. The stopped v1 batch, stored replies/reconstructed inputs, legacy ledger scope and author-confirmed sprint timing are described precisely. The bibliography corrects Chen, Y.-H. and Wagner III, L. T. Fresh checks reproduce the two frozen studies and separately rescore all 160 extension records. See [final verification](final-corrections-verification.json). No forged-metadata attack result or isolated assembler mechanism is claimed.

## Overall judgment

This is a credible, unusually auditable sprint study with a narrow contribution. Its strongest result is that adding trusted purpose information improves both restricted-disclosure and authorized-completion outcomes in one deliberately ambiguous pipeline. Its other useful contribution is methodological: a comparison can confuse missing purpose information with an effect of decomposition, and an assembly-only measure can overlook disclosure across intermediate posts.

I would support presenting the revised paper as a controlled diagnostic study. I would not yet support a general claim that agent teams are less safe than individual agents, that task provenance is a robust defense, or that it outperforms monitoring as a class. The gap to a strong ICML or ICLR empirical paper is primarily experimental breadth and identification of the mechanism, not presentation. Better prose cannot supply the missing experiments.

## Findings checked against the repository

The GitHub connector returned blob identities for forty files in the v2 and task-provenance result directories at the audited commit. Every identity matched the local file bytes. Both official replay tools passed on fresh, clean worktrees at their respective pinned snapshots. No model inference was performed.

| Claim family | Audit result and scope |
|---|---|
| Study 1 volume and reproducibility | 1,040 valid records and 7,670 logged logical calls; all 1,040 stored legacy score triples reproduced. Original Sonnet and same-seed rerun remain separate. |
| Study 1 main outcomes | Neutral strict-policy solo assembly is 19/20 Haiku and 8/10 Sonnet. Explicit solo and repeated-solo assembly is zero in the measured cells. Main-table counts and every outcome cell were rescored. No split condition exceeds the corresponding strict/neutral solo assembly rate. This is descriptive, not an equivalence test. |
| Study 1 relay and control claims | The repository claim checker reproduces relay requests, repeated-seed aggregates, model disclosures and paired contrasts. No-policy neutral swarm assembly is zero, so low assembly alone cannot establish enforcement. The ancillary worker diagnostic reproduces 36 missing-target posts out of 695. |
| Study 2 design and completeness | All 800 planned trials are present and rebuilt from logged replies; 799 are valid. The failed trial is authorized/paraphrase/provenance at seed 3010. The archived analysis reproduces byte-for-byte. |
| Primary effect | Restricted paraphrase recoverability is 45/50 versus 0/50; paired change -90 pp, bootstrap 95% interval [-98, -80], discordant pairs 0/45, exact McNemar p < 0.001. |
| Authorized utility | The complete-pair comparison is 15/49 versus 33/49: +36.73 pp, rounded to +37, interval [20, 53], discordance 21/3, exact p < 0.001. The all-valid local marginal is 15/50. Seed 3010 was a local non-completion, so removing it changes the denominator but not the local numerator. |
| Gates and monitors | Held-out monitor decisions are 792 BLOCK and 3 ALLOW among 795 proposals; neither authorized wording has a completed trial. Restricted paraphrases remain recoverable in 46/50 keyword-gate trials. These are findings about the specified implementations. |
| Pilot erratum | Authorized proposals: 160/161 blocked. All pilot proposals: 320/321 blocked. The one allowed authorized proposal is keyword seed 2018. The shortened appendix had left the denominator scope ambiguous; the revised version gives both. The frozen protocol is preserved. |
| Statistics and scoring | A separate direct scorer agrees with repository assembly and recoverability on all 1,840 study records. Exact paired p-values were recomputed with the binomial formula. Bootstrap intervals use the repository method. Zero events in fifty gives a one-sided 95% upper bound of 5.82% under an iid Bernoulli model, not a universal risk bound. |

The existing claim checker reports 198 current matches, 77 historical matches, two explicitly historical mismatches, fourteen current non-recomputable claims and six historical non-recomputable claims, with zero integrity problems and a successful exit. It audits earlier source documents, not the entire new manuscript. The additional scorer, source-to-document checks and editorial claim mapping cover this edition; its pass is not inferred solely from that legacy checker.

Evidence files: [review calculation script](data-quality/review-check.py), [review results](data-quality/review-results.json), [existing scoped checks](data-quality/check.py), [secondary calculations](secondary-metrics.py), and [verification record](research-review-verification.json). The published [verification guide](https://github.com/wilsonhj/swarm-composition/blob/7d1d0b7db028da46a33b3a8d3fb40b3aba6f41a1/docs/handoffs/verification.md) explains the canonical replays.

## Scientific concerns and editorial response

**The intervention supplies information that the baseline cannot infer.** Local worker prompts and assembler instructions do not encode authorization. Their templates are the same across authorized and restricted objectives, although sampled replies can differ. The provenance condition supplies a trusted answer to that ambiguity. The observed improvement is real within this design, but it is not evidence of discovering hidden intent. The revision states this early and narrows the contribution accordingly.

**Task purpose is not authenticated provenance.** The system prompt declares the objective trustworthy. No signature, chain of custody, authorization service or adversarial metadata validation is tested. The revised related work and limitations define the term and remove any implication that the experiment solves that deployment problem. A system that accepts a forged authorized objective could behave very differently; that remains a hypothesis to test.

**The treatment does not isolate a mechanism.** It adds both an objective and a statement connecting the current contribution to it. There is no objective-only treatment, length-matched irrelevant context, or intervention confined to workers or the assembler. The paper can attribute the observed difference to this prompt package in the tested setting; it cannot distinguish semantic understanding, useful instruction cues, or stage-specific changes.

**The comparison baselines are limited.** The keyword gate is a transparent lexical sanity check: its misses and false blocks follow from its rule and the chosen wordings. The monitor is one frozen prompt, not a tuned representative of monitoring research. Its loss of utility is important, but it does not establish a general safety-utility advantage over monitors. The revised paper explicitly disclaims that ranking.

**Outcome definitions matter to the interpretation.** Study 1's split posts frequently disclose all words without assembling them. In Study 2's authorized paraphrase condition, words are already recoverable in 47/50 local trials, versus 47/49 with provenance, while assembly rises substantially. This suggests a bottleneck in producing the joined output, but does not identify its cause because all actors receive the intervention. Assembly is completion of the specified task, not a comprehensive measure of usefulness. Recoverability is a conservative string-based proxy, not an evaluation of a real attacker.

**Precision is conditional on a narrow task distribution.** Task seeds change lists and positions; they are not independent task families or controlled model-randomness seeds. The studies use one provider family and the main intervention only one model. Repeated relay seeds, one excluded trial, provider-default sampling and the mixed-model original cell remain visible. A negative comparison is not proof of no effect, and a zero cell is not proof of zero risk.

## Comparison with recent academic work

The comparisons below use selected closely relevant ICML and ICLR papers, with newer preprints considered separately. They are methodological benchmarks rather than a claim to have ranked the entire field. Numerical success rates across these different tasks are not directly comparable.

| Paper and publication status | What it contributes as a comparison | Consequence for this paper |
|---|---|---|
| [Adversaries Can Misuse Combinations of Safe Models, ICML 2025](https://proceedings.mlr.press/v267/jones25a.html) | Specifies an adversary combining models with complementary capabilities and evaluates multiple misuse settings. | Our homogeneous synthetic task does not test that mechanism or contradict its results. Retain the useful solo baseline, but do not present it as refuting compositional misuse. |
| [Can LLMs Keep a Secret / ConfAIde, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/08305d8b2ddab98932c163ea73df065f-Abstract-Conference.html) | Grounds disclosure judgments in contextual integrity and varies contextual complexity. | Context-dependent disclosure is established territory. The narrower contribution here is manipulating purpose visibility while separating distributed disclosure from assembly. |
| [AgentHarm, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/c493d23af93118975cdbc32cbe7323f5-Abstract-Conference.html) | Evaluates malicious tool-use tasks with explicit scoring, task diversity and benign counterparts. | Joint safety and useful-performance evaluation is a sound practice, not a novel principle introduced here. This paper's task breadth is far smaller, while its archived replay provides clear internal auditability. |
| [AI Control, ICML 2024](https://proceedings.mlr.press/v235/greenblatt24a.html) | Defines an intentionally subversive model and evaluates protocols against adversarial strategies. | State precisely that our actors are not deliberately subversive. Robust-defense claims would require adversarial evaluation, not only compliance on trusted metadata. |
| [Monitoring Decomposition Attacks with Lightweight Sequential Monitors, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/2985777c8f2152664946ed30deb77291-Abstract-Conference.html) | Evaluates cumulative monitoring on a diverse decomposition dataset with prompt optimization and adversarial tests. | Our frozen monitor prompt is not a replication or competitive baseline for that method. Any future superiority claim needs matched information, budget and benign-task evaluation with a stronger monitor. |

The recent [DeCompBench preprint](https://arxiv.org/abs/2606.13994) and [capability-laundering preprint](https://arxiv.org/abs/2609.15383) further emphasize task diversity and adversarial composition. They support the relevance of the topic but do not validate transfer from harmless passphrases to their threat models. Their status is not presented as equivalent to the peer-reviewed conference papers above.

Four bibliography records now cite verified published versions: Jones et al. (ICML 2025), AgentHarm (ICLR 2025), AI Control (ICML 2024), and sequential monitoring (ICLR 2026). Stable citation keys are retained. The former entries identified real preprints; the change improves currency and publication attribution rather than correcting fabricated references. The submission selects fifteen directly relevant references; the repository retains the broader twenty-nine-reference list and historical supplements.

## Readability and prose

The earlier short edition was accurate in its headline numbers but overcompressed in its literature review and treatment of comparisons. It often asked readers to infer why a caveat mattered. The revision uses a concrete lookup example, defines purpose metadata, makes the shared-policy and differing-information comparisons explicit, and explains why authorized utility and distributed disclosure change the interpretation.

The abstract now gives the primary effect with uncertainty and the paired utility gain. Table 2 uses matched denominators, with the marginal result explained in its caption. Related work is organized around what each strand establishes and what this experiment adds. Peripheral incident summaries and the unimplemented SAE proposal no longer compete with the main argument; the proposal remains disclosed in the appendix. The conclusion states the demonstrated result, its practical evaluation implications and the experiments needed before broader claims.

The existing title is retained to preserve submission identity. It remains longer than ideal for a journal article; a future version could use “Task Purpose and Disclosure in Agent Teams,” provided the submission record is updated consistently. No readability score or claim of human authorship is used as a substitute for reviewing the prose.

## Research priorities after submission

1. **Separate the information treatment.** Cross objective-only, contribution-only, both, and irrelevant context of comparable length. Apply context to workers and assembler separately. Predefine the paired endpoints and analyze intermediate posts as well as the final answer.
2. **Test the trust assumption.** Evaluate missing, false and conflicting purpose claims with a clear account of who can alter each field. Include authorized tasks to distinguish useful resistance from blanket refusal.
3. **Strengthen external validity and baselines.** Use fresh task families and independently chosen wording, multiple provider families, repeated inference and a tuned monitor with comparable information. Add the exact six-call solo relay control before interpreting relay-specific advantages.

These are new studies, not repairs that can be supplied by editing. Until they are run, the paper should remain a carefully bounded study of context and evaluation design.
