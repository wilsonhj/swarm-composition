# 3-Minute Video Script (LA hub)

Hard cap 3:00. Deadline: Sun Nov 8, 10:00 AM Pacific (per https://aialignmentfoundation.org/hackathons/swarm-alignment-2026). Top 15 teams are announced 11:00 AM-12:00 PM PT and give a 10-minute live presentation (12:00-3:00 PM PT). ~150 words/min spoken, so ~420-450 words total. All numbers below are placeholders; fill only from the final run (no pilot numbers).

| Time | Segment | Narration (draft) | On-screen visual |
|---|---|---|---|
| 0:00-0:20 | Hook | "If an AI agent is told not to reveal something, does it matter whether it can tell that its small piece belongs to that secret, and does splitting the job across agents change the outcome?" | Black screen, one line of text; cut to an animated 4-puzzle-piece graphic that clicks together. Title card: "The Composition Gap". |
| 0:20-0:50 | Problem / METR incident | "In August, METR investigated an incident where around twelve hundred OpenAI agents used a shared Artifactory cache like a message board, and about seven hundred joined an attack on Hugging Face. Evaluations mostly look at one agent at a time. We asked a narrower question about what an agent can see." | Screenshot of the METR report title page (https://metr.org/hugging-face-incident-report-aug-2026.pdf) with the sentence about the cache highlighted; simple diagram: many agents -> shared cache. Keep only what the report states. |
| 0:50-1:25 | Design | "We built a safe stand-in: a four-word vault passphrase. Each word is a lookup in one of four separate lists. The rule is a synthetic operator instruction in the prompt, either none or the strict version, 'don't reveal any word.' We vary how much each agent can tell its piece is part of a secret, neutral or explicit. And we vary the structure: one agent alone, with matched numbers of attempts, a pipeline, a four-agent round-robin shared board, and a coordinator relay. Scoring is plain string matching, no AI judge, on held-out seeds." | FIG 1 topologies schematic animated one at a time; a three-row card showing the three framings with the key phrase highlighted; ticker: "2 policies x 2 framings x 8 conditions x [RESULT: n valid] seeds". |
| 1:25-2:15 | Key results | "Result one: [RESULT: under strict, neutral vs explicit framing changes identified parts from X to Y]. Result two: [RESULT: compared with a single agent given the same number of attempts, the pipeline and the shared board change the assembled rate from A to B, with CIs]. Result three: in the relay, [RESULT: informed vs uninformed coordinators requested pieces in P% vs Q% of valid runs]. Report null results as null." | FIG 2 heatmap (framing x condition) with the key cells circled; FIG 3 swarm-size line plot; TAB 3 relay table with two numbers highlighted. One result per ~15 seconds; show n and a CI. |
| 2:15-2:40 | Implication | "Our reading, [RESULT-dependent, tentative]: if refusal tracks what an agent can see, then in multi-agent systems what the coordinator knows and what the shared board shows matter. That would motivate checks on context propagation and shared channels, not just per-agent evaluation. This is a hypothesis for future work, not something we tested as a defence." | Diagram: context flows as arrows between agents with a monitor icon on the shared board. Caution line on screen: "Hypothesis; benign proxy; synthetic restriction; [RESULT: n]". |
| 2:40-3:00 | Ask / close | "This is a benign proxy with real limits: small scale, a synthetic restriction rather than trained-in refusal, one model family so far, no tools. We want help extending it to other model families, real tool use, and testing monitors. Code, prompts and the report are linked below. Thanks." | Limitations bullet strip (3 bullets), then repo QR / URL [TODO: repo URL], team name, hub, track. |

## Word budget
Hook 45 | Problem 70 | Design 110 | Results 120 | Implication 60 | Close 45 = ~450 words. Trim the design segment first if you run over.

## Dos and don'ts
- Do not state any pilot number; use final-run numbers only, and show valid n. Never say agents that refuse alone become unsafe together unless the frozen run shows it against matched baselines.
- Do not show or speak the actual passphrase words from the real run if they are reused anywhere else.
- Do not imply a real attack was reproduced; say "benign proxy" aloud at least once.
- Say "consistent with" when presenting the context-visibility interpretation.

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
