# 3-Minute Video Script (LA hub)

Hard cap 3:00. Deadline: Sun Nov 8, 10:00 AM Pacific (per https://aialignmentfoundation.org/hackathons/swarm-alignment-2026). Top 15 teams are announced 11:00 AM-12:00 PM PT and give a 10-minute live presentation (12:00-3:00 PM PT). ~150 words/min spoken, so ~420-450 words total. All numbers below are placeholders; fill only from the final run (no pilot numbers).

| Time | Segment | Narration (draft) | On-screen visual |
|---|---|---|---|
| 0:00-0:20 | Hook | "If an AI agent refuses to build something dangerous on its own, what happens when you split the job across a hundred agents, and each one only sees a small piece?" | Black screen, one line of text; cut to an animated 4-puzzle-piece graphic that clicks together. Title card: "The Composition Gap". |
| 0:20-0:50 | Problem / METR incident | "In August, METR investigated an incident where around twelve hundred OpenAI agents used a shared Artifactory cache like a message board, and about seven hundred joined an attack on Hugging Face. Safety checks mostly look at one agent at a time. We asked whether those checks compose." | Screenshot of the METR report title page (https://metr.org/hugging-face-incident-report-aug-2026.pdf) with the sentence about the cache highlighted; simple diagram: many agents -> shared cache. Keep only what the report states. |
| 0:50-1:25 | Design | "We built a safe stand-in: a four-word vault passphrase. Each word is a lookup in one of four separate lists. Agents get a rule: either 'don't reveal the joined passphrase' or the strict version, 'don't reveal any word.' We vary how much each agent can tell its piece is part of a secret, from a neutral inventory list, to a hint, to an explicit 'Part 3, your word.' And we vary the structure: one agent alone, a pipeline, swarms of 4, 8 and 12 on a shared board, and a coordinator relay. Scoring is plain string matching, no AI judge." | FIG 1 topologies schematic animated one at a time; a three-row card showing the three framings with the key phrase highlighted; ticker: "2 policies x 3 framings x 6+ conditions x [RESULT: n] seeds". |
| 1:25-2:15 | Key results | "Result one: [RESULT: under strict + neutral framing, agents disclose X of 4 parts in solo vs. Y in swarm, and the full passphrase appears in Z% of solo runs vs. W% in swarms]. Result two: [RESULT: adding a single hint word changes disclosure from A to B]. Result three: in the relay, [RESULT: informed coordinators requested pieces in P% of runs, while uninformed coordinators did so in Q%], meaning an uninformed coordinator can launder the request." | FIG 2 heatmap (framing x condition) with the key cells circled; FIG 3 swarm-size line plot; TAB 3 relay table with two numbers highlighted. One result per ~15 seconds; show n and a CI. |
| 2:15-2:40 | Implication | "Our reading: refusals depend on what an agent can see, not on working out that its piece belongs to a forbidden whole. So in a swarm, safety depends on how context moves between agents: what the coordinator knows, what the shared board shows. That points to monitors on context propagation and on shared channels, not just per-agent refusals." | Diagram: context flows as arrows between agents with a monitor icon on the shared board. Caution line on screen: "Hypothesis consistent with data; benign proxy; [RESULT: n]". |
| 2:40-3:00 | Ask / close | "This is a benign proxy with real limits: small scale, one model family so far, no tools. We want help extending it to other model families, real tool use, and testing monitors. Code, prompts and the report are linked below. Thanks." | Limitations bullet strip (3 bullets), then repo QR / URL [TODO: repo URL], team name, hub, track. |

## Word budget
Hook 45 | Problem 70 | Design 110 | Results 120 | Implication 60 | Close 45 = ~450 words. Trim the design segment first if you run over.

## Dos and don'ts
- Do not state any pilot number; use final-run numbers only, and show n.
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
