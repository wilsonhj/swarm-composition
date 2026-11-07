# Appendix A: Limitations and Dual-Use / Ethical Considerations

DRAFT. Statements in [brackets] depend on final results or decisions; revise before submission.

## A.1 Limitations

**Benign proxy vs. real harm.** The forbidden artifact is an arbitrary four-word "vault passphrase". Models may treat a made-up passphrase very differently from content that is harmful in the world (malware, weapons uplift, exfiltration). Our results therefore measure whether context visibility affects a policy-following behavior; they do not show the same rates would hold for genuinely dangerous artifacts, for which refusal training is typically stronger and may key on different features. Results should be read as a mechanism probe, not a risk estimate. The policy is also operator-style (system prompt), not trained-in refusal, so we are testing instruction-following under a restriction more than safety-trained refusal.

**String-match scoring.** Scoring is exact string match on the words and the joined passphrase. This avoids LLM-judge noise but misses paraphrase, encoding, partial reconstruction (e.g., initials, reordered or spelled-out words), and disclosure in forms the matcher does not normalize. Reported disclosure is a lower bound on information leakage. It also counts a word as disclosed even if it was reported at the wrong list position [DECIDE and state how position errors are handled].

**Small n.** [RESULT: n seeds per cell]. Pilot runs used 3-10 seeds and were used only to select conditions; they are not reported as results. Even in the full run, many cells have wide confidence intervals, interactions across policy x framing x condition x model are underpowered, and we did not correct for all comparisons made [state method].

**Prompt sensitivity and surface cues.** Framing effects may reflect specific lexical cues ("access-code", "vault", "Part k") rather than a general property of context visibility. We tested three framings; we did not sweep paraphrases. Findings that depend on single words should be treated as cue-sensitivity, and our interpretation (refusals track visible context, not inference of the forbidden whole) is a hypothesis consistent with the data, not a mechanistic demonstration.

**System-prompt policy confound.** The `strict` policy text names the "vault passphrase" in every agent's system prompt, including agents we describe as "uninformed" or "neutral". Those agents are therefore not fully uninformed: they have been told a secret of that type exists. This weakens the neutral-framing and relay_uninformed contrasts. [RESULT: ablation with a policy text that does not name the artifact, if completed; otherwise state not completed.]

**Single provider family.** Main results use Claude Haiku 5.5 and Sonnet 5.5. Other families may differ substantially. [RESULT: cross-model OpenRouter runs, which models, n; otherwise "not completed"]. We do not claim generality across providers.

**Sequential turn-taking and short horizons.** Swarm agents act in a fixed sequential order over 3 rounds on a shared board. Real swarms are asynchronous, larger, long-running, and heterogeneous, with agents that join and leave. The METR-described incident involved on the order of 1,200 agents; our largest condition is 12. Behavior may change with scale, duration, and memory.

**Position-reporting errors by workers.** Workers sometimes report the word at the wrong position or the wrong list; this adds noise to parts_disclosed and joined [RESULT: error rate]. Joined rates in particular can understate intent to comply.

**No tool use.** Agents have no tools, filesystem, network, or persistent cache. The incident motivating this work involved agents using a real shared artifact store. Our "board" is an abstraction and omits permissions, rate limits, logging, and side channels.

**Other.** Single task structure (lookup-and-concatenate); no adversarial optimization of prompts; no human baseline; the strict/join policies are our own wording. We did not evaluate any defense, so Section 5 defense ideas are untested suggestions.

## A.2 Dual-Use Considerations

**Could this help someone launder harmful requests through decomposition?** Possibly in principle: a paper showing that splitting work across agents can change what individual agents will do is conceptually a recipe for decomposition attacks. We assess the marginal uplift as low because (i) decomposition attacks on single models and multi-agent systems are already discussed in the literature [cite from `../docs/research/related-work.md`], (ii) our task is a toy with no harmful content, (iii) the central finding is about which contextual cues change behavior, a coarse insight rather than a working exploit, and (iv) the METR incident report already documents real-world multi-agent coordination. We still treat the risk as non-zero and take the steps below.

**Why a benign proxy.** We deliberately avoid any genuinely harmful artifact. A passphrase of four arbitrary words lets us measure composition behavior with exact scoring, run many seeds cheaply, and publish prompts, transcripts, and code without handing anyone harmful content. The cost is external validity (A.1).

**What we withhold or do not do.**
- We do not test or publish decompositions of real harmful tasks (CBRN, cyber offense, malware, exfiltration), or prompts tuned to evade a deployed model's refusal for such tasks.
- We do not publish an optimized "laundering" prompt library. Relay examples in Appendix B are limited to the benign proxy and include only what is needed to reproduce the measurement. [DECIDE: whether the uninformed-coordinator laundering transcript is included in full or summarized.]
- We do not release attack scaffolding aimed at real systems or real infrastructure (e.g., any code that targets package registries, caches, or model hubs).
- We report no vendor-specific bypasses beyond the aggregate rates needed to interpret the results.

**Responsible-disclosure stance.** If a finding looks like a transferable weakness in a specific deployed model or product (for example, a repeatable laundering route for a restricted behavior), we will notify the relevant provider [Anthropic and any OpenRouter-tested vendors] before broader publicization of details, and will delay releasing the specific prompts until they have had a reasonable chance to respond. [DECIDE: the timeline, and who on the team owns the notification.] Our current results involve only a benign task, so we do not expect this to be triggered, but we note the process.

**Defensive uses and intended benefit.** The intended use is to inform defense:
- Context-propagation monitors that track what each agent can see (task framing, board contents, coordinator knowledge) and flag when many individually-innocuous contributions compose into a restricted artifact.
- Board-level / shared-channel monitors on shared stores (the cache-as-message-board pattern from the METR report) that check aggregates, not only individual messages.
- Coordinator-level intent checks: our relay conditions test whether a coordinator that knows the goal still requests pieces and whether an uninformed one can be used to launder a request, which bears on where to place intent checks in orchestration frameworks.
- Evaluation design: per-agent refusal evaluations are insufficient for swarm deployments; composition-aware evals should be added to testbeds. Our harness is a minimal example.

**Other ethical considerations.** No human subjects or personal data. API use complied with provider terms of service; the "forbidden" content is benign by construction, so no safety policies were circumvented in a harmful way. Compute and cost: [RESULT: total tokens / spend]. Cross-model runs via OpenRouter send only the benign prompts. Credit: pre-sprint work is identified in the main text (Section 3.6).

**Net assessment.** We believe the benefits (identifying a measurable gap and pointing at context propagation as a control surface) outweigh the marginal risk, given the benign proxy, the existing literature, and the withheld material above. [Revisit if the final results show a strong, transferable laundering effect.]
