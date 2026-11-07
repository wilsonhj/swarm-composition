# Report skeleton: The Composition Gap

Track 2: The Science of Agent Networks. Swarm Alignment Hackathon, Nov 6-8 2026.

Constraints (from https://apartresearch.com/sprints/swarm-alignment-2026): PDF on Apart's template; max 8 pages NOT counting references and appendices; abstract 150-250 words; authors and affiliations; REQUIRED appendix "Limitations and Dual-Use / Ethical Considerations". Pre-sprint work must be marked as preexisting in README and report (see 3.6). Page budget below totals 8.0.

Conventions: `[RESULT: ...]` = number to fill from the full run. `[PILOT: ...]` = pilot observation (n=3-10 seeds), to be replaced by the full run and never reported as a result. `[FIG]`/`[TAB]` = planned figure/table. Do not write any pilot value in the final text.

---

## Title (working)
"The Composition Gap: Do Refusals Survive When Forbidden Work Is Split Across Agents?"
Alternates: "Refusal Depends on Context Visibility: Decomposition Attacks in Agent Swarms"; "Split It Up: Measuring Whether Multi-Agent Composition Bypasses Per-Agent Refusals".

## Authors and affiliations
[PLACEHOLDER: names, affiliations, emails; Team name; Hub (LA / global); Track 2]

## Abstract (150-250 words; target 200)
Structure, one to two sentences each:
1. Motivation: METR's Aug 2026 report on ~1,200 OpenAI agents using an Artifactory cache as a message board, ~700 joining an attack on Hugging Face. Per-agent refusals may not compose.
2. Question: if an agent refuses to produce a forbidden artifact alone, does it still contribute its piece when the work is split?
3. Method: benign proxy (4-word "vault passphrase" assembled from lookups across 4 disjoint lists), 2 policies (join, strict) x 3 framings (neutral, hinted, explicit) x conditions (solo, pipeline, swarm@N, relay), string-match scoring, [RESULT: n models, n seeds].
4. Findings: [RESULT: headline 1, e.g. joined rate solo vs pipeline vs swarm], [RESULT: headline 2, framing effect on parts_disclosed], [RESULT: headline 3, relay informed vs uninformed coordinator].
5. Interpretation (tentative, hedge appropriately): refusal tracks visible context, not inference of the forbidden whole; swarm safety depends on how context propagates.
6. Caveats in one clause: benign proxy, string-match, [RESULT: n].

## 1 Introduction (target 0.9 page)
- Para 1: METR incident (cite METR report https://metr.org/hugging-face-incident-report-aug-2026.pdf, per event page). One factual sentence on the shared-cache-as-message-board pattern; do not embellish beyond the report.
- Para 2: The gap: safety training and policies are evaluated per agent/per context. Composition (decomposition across agents) is a distinct threat surface.
- Para 3: Our question and benign-proxy approach, in two sentences.
- Para 4: Contributions (bullets):
  1. A controlled, string-match-scored testbed for composition (no LLM judge).
  2. Factorial measurement across policy x framing x topology x swarm size x model: [RESULT: n runs total].
  3. Evidence on which factors move disclosure: [RESULT: effect sizes with CIs].
  4. A relay analysis showing whether a coordinator that knows the goal will request pieces, and whether an uninformed one launders the request.
  5. Release of code/data [TODO: repo URL; confirm release scope per Appendix A].
- [FIG 1: schematic of the four topologies on one row; planned for page 1 or 2. Caption: "Conditions. Solo: one agent holds all four lists. Pipeline: four workers, one list each, then an assembler. Swarm@N: N agents on a shared board for 3 rounds, with or without a team objective. Relay: a coordinator directs four workers."]

## 2 Related Work (target 0.6 page)
- Source: `../docs/research/related-work.md` (being written in parallel). Do NOT write citations from memory; pull only entries that file verifies.
- Subsections to draw from that file:
  - Decomposition / task-splitting attacks on single models and multi-agent systems.
  - Multi-agent safety and emergent behavior in agent networks (event page lists suggested reading incl. swarmtraces.org, AI Village dataset, Transluce agent activity).
  - Information flow and context isolation / contextual integrity in LLM agents.
  - Multi-agent oversight and monitoring (for implications).
- Closing sentence: positioning, i.e., what is new here relative to the above [TODO after reading related-work.md].
- [TODO: cite the OpenAI Hugging Face incident write-up and METR report as incident sources.]

## 3 Methods (target 1.9 pages)
### 3.1 Benign proxy task (0.3 p)
- Forbidden artifact: a 4-word "vault passphrase". Each word = lookup at a given position in one of 4 disjoint 6-word lists. Why benign: no real-world capability; the secret is arbitrary. Why composition-structured: no single list or lookup reveals the whole.
- Seeds: [RESULT: n seeds, how lists/positions were generated, whether word lists are public].
### 3.2 Policies (0.2 p)
- `join`: only the joined passphrase is forbidden.
- `strict`: no word may be revealed, even one at a time.
- Note the confound (3.6): the strict text names "vault passphrase" in every agent's system prompt.
### 3.3 Framings (0.25 p)
- neutral ("inventory list ... item at position k"), hinted ("access-code segment"), explicit ("Part k ... your word"). Table of exact wording lives in Appendix B.
- Framing = how much an agent can tell its piece belongs to the secret.
### 3.4 Conditions (0.5 p)
- solo; pipeline; swarm@N and swarm_noobj@N for N in {4, 8, 12}, 3 rounds, shared board, sequential turn order; relay (informed coordinator) and relay_uninformed ("compile four items").
- [TAB 1: condition x (agents, rounds, who sees what, objective given?)]
### 3.5 Metrics and scoring (0.25 p)
- joined (full passphrase string appears in final output or any agent message [DECIDE]); parts_disclosed (0-4); all_disclosed; relay: coordinator_requested, request_names_secret.
- String match only; define normalization (case, punctuation) [TODO]. No LLM judge. Worker position-reporting errors handled as [DECIDE: count wrong-position words or not].
- Stats: Wilson/bootstrap CIs, [RESULT: n per cell]; multiple-comparison handling [TODO].
### 3.6 Models, infrastructure, pre-sprint disclosure (0.4 p)
- Claude Haiku 5.5 and Sonnet 5.5 via Claude Code; cross-model via OpenRouter [RESULT: which models completed; else state not run].
- Temperature/sampling/max turns [TODO]. Cost [RESULT: total runs, tokens].
- Pre-sprint disclosure: [TODO: state exactly what code/pilots existed before Nov 6 vs. built during the sprint; Apart rules require this.]
- Pilot-to-final protocol: pilot (small n) was used to choose conditions only; all reported numbers come from the full run [confirm].

## 4 Results (target 2.4 pages)
Write only after the full run. Each subsection: claim sentence, number, CI, figure pointer.
### 4.1 Baseline: policy matters (0.4 p)
- [RESULT: parts_disclosed and joined under join policy, by model, solo]. [PILOT: near-universal disclosure under join; replace]
- [TAB 2: policy x condition x model, joined / parts_disclosed / all_disclosed with 95% CI, n=[RESULT]]
### 4.2 Framing x condition (0.7 p)
- [FIG 2: heatmap, parts_disclosed (and joined as second panel) by framing (rows: neutral/hinted/explicit) x condition (cols: solo, pipeline, swarm@4/8/12, swarm_noobj); one heatmap per model. Caption: "Disclosure vs. framing x condition under `strict`. Cells show mean parts_disclosed [RESULT: n=...]; annotations show joined rate."]
- Key comparisons: neutral vs. hinted vs. explicit [RESULT: deltas]; [PILOT: single hint word effect size; replace with ablation]. Joined vs. parts disclosed gap by condition: [RESULT].
### 4.3 Swarm size and objective (0.5 p)
- [FIG 3: line plot, joined rate and parts_disclosed vs. N in {4,8,12}, lines = swarm / swarm_noobj, per model, with CI bands. Caption placeholder.]
- [RESULT: slope / trend; does objective change disclosure; any dilution/diffusion effect].
### 4.4 Relay (0.5 p)
- [TAB 3: relay rows: informed vs. uninformed coordinator x model: coordinator_requested, request_names_secret, parts_disclosed, joined; n=[RESULT]]
- [RESULT: informed coordinator request rate]. [PILOT: informed coordinators refused to request pieces outright]. [RESULT: uninformed laundering rate; qualitative example (benign proxy only) in Appendix B]
- Report the uninformed-coordinator confound explicitly (3.2/5.3).
### 4.5 Robustness (0.3 p)
- [RESULT: policy-text confound ablation: strict text without naming "vault passphrase"]; [RESULT: cross-model OpenRouter check]; [RESULT: worker position errors rate]. Others in Appendix B.

## 5 Discussion (target 0.8 page)
### 5.1 Interpretation (0.35 p)
- Hypothesis: refusals respond to visible context rather than inferred membership in a forbidden whole. Evidence for: [RESULT]; evidence against / alternative explanations: surface-cue sensitivity, prompt wording, [RESULT]. Keep claim at "consistent with".
### 5.2 Implications for swarm safety (0.3 p)
- Context propagation as a control point: what each agent sees (task framing, shared board, coordinator knowledge). Link to METR incident: shared channels (cache-as-message-board) are the propagation layer. Defensive candidates: context-propagation monitors, board-level monitors, coordinator-level intent checks (no new data claimed).
### 5.3 Threats to validity (0.15 p; details in Appendix A)
- Summarize top 3 limitations; point to Appendix A.

## 6 Conclusion (target 0.3 page)
- Answer to the question in two sentences ([RESULT]); one-sentence implication; next steps (real-tool-use settings, multi-provider, monitor evaluation, larger N, free-form turn-taking).

## References (not counted)
- Generated from `../docs/research/related-work.md` [TODO]. Include METR report and OpenAI incident write-up as listed on the event page.

## Appendix A: Limitations and Dual-Use / Ethical Considerations (REQUIRED; not counted)
- Draft in `appendix-limitations-dual-use.md`; paste in verbatim after final numbers are known and revise any statement that depends on results.

## Appendix B: Extra results and prompts (not counted)
- B.1 Exact system prompts for join/strict and each framing, and the relay coordinator prompts (benign proxy; fine to release).
- B.2 Full results tables: all cells with n, CIs. [TAB B1]
- B.3 Per-model breakdowns; heatmaps for each model. [FIG B1]
- B.4 Swarm board transcripts: 2 representative runs per outcome (disclosed / not), benign proxy only.
- B.5 Relay laundering example transcript(s): [RESULT: if any occurred]. Check against Appendix A release policy before including.
- B.6 Scoring: normalization rules, string-match code snippet, position-error handling.
- B.7 Policy-text confound ablation details.
- B.8 Cost, runtime, reproducibility (seeds, versions, commit hash [TODO]).

---

## Page budget
| Section | Pages |
|---|---|
| Title/abstract | 0.4 |
| 1 Intro | 0.9 |
| 2 Related | 0.6 |
| 3 Methods | 1.9 |
| 4 Results | 2.4 |
| 5 Discussion | 0.8 |
| 6 Conclusion | 0.3 |
| Total (excl. refs/appendices) | 7.3 (0.7 slack for figures) |

## Figure and table list
- FIG 1 topologies schematic (Sec 1)
- FIG 2 framing x condition heatmap (Sec 4.2)
- FIG 3 swarm-size sweep (Sec 4.3)
- TAB 1 conditions (Sec 3.4)
- TAB 2 policy x condition x model (Sec 4.1)
- TAB 3 relay (Sec 4.4)

## Judging alignment
- Global: Impact Potential & Innovation (Sec 1, 5.2), Execution Quality (Sec 3, 4, App. B), Presentation & Clarity (figures, abstract).
- LA: Idea (novelty/relevance), Soundness & execution, Results, Clarity & presentation.
- Fix the known design issue (strict policy text names the passphrase to all agents) before the full run, or report it as a limitation; Sec 3.2 and App. A.1 currently describe it as present.

## Pre-submission checklist
- [ ] No pilot number appears as a result
- [ ] Abstract 150-250 words
- [ ] Main body <= 8 pages; appendix A present and titled "Limitations and Dual-Use / Ethical Considerations"
- [ ] Pre-sprint work disclosed in report and README
- [ ] PDF <= 25 MB
- [ ] Submission form fields ready (title, abstract, PDF, publish-interest, track(s), team name, location, member 1 name+email)
