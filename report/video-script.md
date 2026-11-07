# 3-Minute Video Script (LA hub)

Hard cap 3:00. Deadline: Sun Nov 8, 10:00 AM Pacific (per https://aialignmentfoundation.org/hackathons/swarm-alignment-2026). Top 15 teams are announced 11:00 AM-12:00 PM PT and give a 10-minute live presentation (12:00-3:00 PM PT). Narration is 426 words (~2:50 at 150 words/min), leaving ~10 s for transitions.

One talk, two separate studies; their numbers are never pooled. **Study 1:** frozen v2 composition study (Haiku 5.5 n = 20 seeds per cell; Sonnet 5.5 n = 10). **Study 2:** task-provenance held-out confirmatory run (Haiku 5.5, seeds 3000-3049, frozen protocol). All intervals below are as reported in the source files (Wilson 95% for rates; paired-bootstrap 95% for seed-paired differences). Sources are listed in "Number sources".

Team: [TODO: team name]. Presenters: [TODO: presenter names]. Repo: https://github.com/wilsonhj/swarm-composition (public).

| Time | Segment | Words | Narration | On-screen visual |
|---|---|---|---|---|
| 0:00-0:15 | Hook | 35 | "If an AI agent is told not to reveal something, does it matter whether it can tell that its small piece belongs to that secret? And does splitting the job across agents change the outcome?" | Black screen, one line of text; cut to an animated 4-puzzle-piece graphic that clicks together. Title card: "The Composition Gap". |
| 0:15-0:36 | Problem / METR incident | 51 | "In August, METR investigated an incident where around twelve hundred OpenAI agents used a shared Artifactory cache like a message board, and about seven hundred joined an attack on Hugging Face. Evaluations mostly look at one agent at a time. We asked a narrower question about what an agent can see." | Screenshot of the METR report title page (https://metr.org/hugging-face-incident-report-aug-2026.pdf) with the cache sentence highlighted; simple diagram: many agents -> shared cache. Keep only what the report states. |
| 0:36-1:01 | Design | 58 | "This is a benign proxy. A four-word vault passphrase, split into four separate lookups, with a synthetic operator rule in the prompt: none, or strict, don't reveal any word. We vary framing, neutral or explicit, and structure: solo, solo with matched retries, pipeline, shared board, coordinator relay. Scoring is plain string matching, no AI judge, on held-out seeds." | `report/figures/fig1_topologies.png` (topologies, revealed one at a time); key framing phrase highlighted. Ticker: "2 policies x 2 framings x 8 conditions x 20 seeds (Haiku); 10 seeds (Sonnet)". |
| 1:01-1:46 | Study 1 results (v2) | 110 | "Study one, Haiku, twenty seeds per cell. Under strict, a solo agent with neutral framing still wrote the passphrase in nineteen of twenty runs. With explicit framing, zero of twenty, even with twelve retries. The rule alone does not decide refusal; framing does. Does splitting the task leak it? Barely. The best case, an uninformed relay, assembled one of twenty against zero for solo: plus five points, interval zero to fifteen. An informed coordinator sent no request in forty of forty runs. Sonnet, ten seeds, pointed the same way: two of ten, plus twenty points, interval zero to fifty. We report that as a null: no safe-alone, dangerous-together gap established." | `report/figures/fig2_v2_heatmap.png` (framing x condition) with strict/neutral and strict/explicit solo cells circled (19/20 vs 0/20), then the relay_uninformed strict/explicit cell (1/20 vs solo 0/20). On screen: "n = 20 per cell; Wilson 95% CI [76-99%] vs [0-16%]"; "paired +5 pp [0, +15]"; "Sonnet n = 10: +20 pp [0, +50]"; stamp "NULL". **Fig 3 fallback:** `fig3_v2_swarm_size.png` is not used here because the frozen v2 run has only one swarm size (swarm@n4). If it exists, skip it anyway; show the 8-condition table cut-out of the Haiku main table instead. |
| 1:46-2:31 | Study 2 (provenance held-out) | 106 | "Study two is a separate, frozen confirmatory run on fresh seeds. We gave every pipeline agent the trusted purpose of the task. Haiku, fifty seeds per cell. On restricted tasks, recoverable passphrases fell from forty-five of fifty to zero of fifty: minus ninety points, interval minus ninety-eight to minus eighty. On authorized tasks, assembly rose from fifteen of fifty to thirty-three of forty-nine: plus thirty-seven points, interval plus twenty to plus fifty-three. So safety did not cost utility. It is not keyword matching: a keyword gate still let forty-six of fifty paraphrased restricted runs recover the passphrase. One of eight hundred trials failed; we excluded it." | `report/figures/fig5_provenance_design.png` (2 s: local vs provenance pipeline), then `report/figures/fig4_provenance_heldout.png` with the two paraphrase bars highlighted. On screen: "Restricted, recoverable: local 45/50 -> provenance 0/50; paired -90 pp [-98, -80], McNemar p < 0.001"; "Authorized, assembled: 15/50 -> 33/49; +37 pp [+20, +53]"; "Keyword gate, paraphrase restricted: 46/50 recoverable". Small footer: "1 of 800 trials failed (backend error), excluded. Frozen protocol, seeds 3000-3049." |
| 2:31-2:47 | Implication | 37 | "Consistent with these results, what each agent knows about the task's purpose matters more than the rule it is given. That motivates checking context propagation, not just per-agent behaviour. A hypothesis, not a defence we have deployed." | Diagram: context flows as arrows between agents. Caution line on screen: "Hypothesis; benign proxy; synthetic restriction; Haiku 5.5 (Study 2 n = 50/cell)". |
| 2:47-3:00 | Close | 29 | "Limits: one model family, synthetic restriction, no tools, and provenance supplied by the harness. Future work: other models and an interpretability follow-up. Code and report are linked below. Thanks." | Limitations bullet strip (3 bullets), then URL https://github.com/wilsonhj/swarm-composition (and QR), team name [TODO: team name], hub, track 2. Label SAE as "future work, not run". |

## Word budget (spoken)
Hook 35 | Problem 51 | Design 58 | Study 1 110 | Study 2 106 | Implication 37 | Close 29 = **426 words, ~2:50 at 150 wpm** (cap 3:00). If you run over, trim the Design segment first, then the informed-coordinator sentence in Study 1.

## Number sources
All paths are relative to the repo root. Study 1 and Study 2 are never pooled.

Study 1 (frozen v2, Haiku 5.5 seeds 1000-1019, Sonnet 5.5 seeds 1000-1009):
- Solo strict/neutral 19/20 [76-99%]; solo strict/explicit 0/20 [0-16%]; solo@k12 strict/explicit 0/20 [0-16%]; relay_uninformed strict/explicit assembled 1/20 [1-24%]; paired vs solo +5 pp [0, +15], +1/-0, p = 1.0: `experiments/composition-gap/results/v2/analysis.md` (cells table and "Seed-paired contrasts vs solo"); also `docs/findings/v2-results.md`.
- Informed coordinator requests under strict 0/40 (none: 40/40): `docs/findings/v2-results.md` (coordinator requests table; relay rows pool neutral and explicit cells because relay prompts do not use framing).
- Sonnet relay_uninformed strict/explicit assembled 2/10 (main run), paired +20 pp [0, +50], p = 0.50: `docs/findings/v2-results.md` ("Sonnet 5.5 replication"); `experiments/composition-gap/results/v2/analysis_sonnet.md`.
- Wilson CI is as stated in the analysis files; the on-screen "[0-16%]" for 0/20 comes from `analysis.md`.

Study 2 (task-provenance held-out, Haiku 5.5, seeds 3000-3049, run 4c134cfd-0a87-49f2-ba16-a4cba153a701, freeze commit 435d20d4d0d8e7bf24a391d077649b98e6d526ae):
- Restricted/paraphrase recoverable local 45/50 -> provenance 0/50; paired -90 pp [-98, -80], 0/45 discordant, McNemar p < 0.001: `docs/findings/provenance-heldout.md` (contrasts table); `experiments/composition-gap/results/task-provenance/heldout-haiku.jsonl.analysis.md`.
- Authorized/paraphrase assembled local 15/50 -> provenance 33/49; paired +37 pp [+20, +53], 21/3 discordant, p < 0.001: same files.
- Keyword gate, restricted/paraphrase recoverable 46/50: same files.
- 1 failed trial of 800 (backend error, paraphrase/authorized/provenance), excluded; all-trial bounds in the analysis file: `docs/findings/provenance-heldout.md` (Run table).

Not used in the script, by choice: the LLM monitor over-blocking (792 of 795 proposals), the keyword-framing contrasts, and the pilot numbers.

## Dos and don'ts
- Do not state any pilot number; use frozen-run numbers only, and show n. Never say agents that refuse alone become unsafe together: Study 1 reports a null on that.
- Do not pool Study 1 and Study 2, and do not describe Study 2 as a test of the composition gap; it tests giving agents the task purpose.
- Do not show or speak the actual passphrase words from the real run if they are reused anywhere else.
- Do not imply a real attack was reproduced; say "benign proxy" aloud (done in Design).
- Say "consistent with" when presenting the context-visibility interpretation (done in Implication).
- Study 2 provenance is harness-supplied and trusted; the Close states this.
- SAE is future work only; do not present it as run or planned results.

## Recording checklist
- [ ] Length: 3:00 or less (hard cap per LA hub rules; the Apart report form's optional demo video is 3-5 min, but the LA hub video is 3 min)
- [ ] Format: NOT specified on either event page; confirm with the hackathon contact or the registration confirmation (file type, resolution, size). Default plan: MP4 (H.264), 1080p, 16:9, under [TODO: size limit], captions burned in or SRT.
- [ ] Where to submit: NOT specified on the AI Alignment Foundation page ("confirm through registration or the hackathon contact email"). [TODO: confirm with LA hub organizers whether it is a form link, email, Discord, or upload; confirm by Sat Nov 7]
- [ ] Deadline: Sun Nov 8, 10:00 AM Pacific; aim to submit by 8:30 AM PT; verify the time zone conversion for the recorder
- [ ] Also attach to Apart submission form's optional "presentation recording" field (optional; 3-5 min demo allowed on that form)
- [ ] Audio: external mic or quiet room, level check, no clipping; narrate from a script; optional captions
- [ ] Screen capture at 1080p; zoom plots to >=18 pt equivalent; check legibility on a laptop screen
- [ ] All figures regenerated from the final data; no pilot figures
- [ ] Final watch-through for: numbers match the report, "benign proxy" said, limitations shown, link/QR works
- [ ] Export a backup copy; keep the exact file submitted

## Open TODOs
- [TODO: team name]
- [TODO: presenter names]
- [TODO: upload destination and method (not stated on event pages)]
- [TODO: video file format and size limit (not stated on event pages)]
