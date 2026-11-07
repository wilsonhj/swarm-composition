# Cowork research session notes (Nov 6–7, 2026)

These notes are a delta: they record only what a separate Claude Cowork research session found that this repo does not already contain. The METR incident, dataset access, deadlines and rules are already covered in more detail (and more carefully sourced) in `docs/research/metr-incident.md`, `docs/dev/datasets.md` and `docs/hackathon/`. Where the two disagree, trust those files.

Verification status: everything below came from a web-fetch subagent. Items marked **[summary]** came from the tool's model-written summary of the part of the page it could not show verbatim. Re-fetch them before citing in the report (repo rule: cite only fetched sources).

## 1. Global judge panel (Apart page)

Source: https://apartresearch.com/sprints/swarm-alignment-2026 (fetched 2026-11-07). **[summary]** The roster sat beyond the verbatim cutoff, so the names, affiliations and the count of about 50 below are unverified.

The panel leans heavily toward security, identity and production engineering:

| Background | Judges |
|---|---|
| Red teaming and security | Mateusz Dziemian (Gray Swan), Reworr (UK AISI red team via MATS), Nirav Patel (Okta), Casey Barkan (RAND) |
| Large-company engineering | Microsoft, Meta, Amazon (×3), Salesforce (×2), Uber, PayPal, Snowflake, Intuit, Box, Pega, Jane Street |
| Research | Dane Malenfant (Mila), Amelie Knecht (Stuttgart / MATS), Jady Pamella (Aarhus), Andrey Anurin and Kunvar Thaman (Apart), George Ingebretsen (AI Village) |

**[summary]** About 50 judges are listed in total. This panel scores the global round: a written report, after the weekend, with no live Q&A. Its three 1–5 criteria are already recorded verbatim in `docs/hackathon/judging-and-rules.md`. The LA hub round has a different panel and four different criteria; these notes do not describe that panel.

**What this implies for framing.** The provenance result reads naturally as an access-control finding for this audience. Numbers are from the frozen held-out run (Haiku 5.5, seeds 3000–3049, one pipeline, harness-supplied trusted provenance; `docs/findings/provenance-heldout.md`):

- In this fixed pipeline, withholding the overall purpose leaves restricted recoverability at 45/50 with paraphrase wording (49/50 with keyword wording). This comparison does not isolate an effect of decomposition: both conditions use the same pipeline, and paired authorized/restricted local prompts are identical.
- In this Haiku run, supplying trusted task metadata reduces observed restricted recoverability to 0/50 in both wordings, while authorized assembly rises from 15/50 to 33/49 (paraphrase; one failed trial) and from 12/50 to 48/50 (keyword). These observations do not establish zero underlying risk or a general absence of utility costs.
- For these tested wordings, provenance outperforms the keyword gate: the gate leaves 46/50 paraphrased restricted runs recoverable and cuts authorized keyword assembly to 0/50.
- An LLM monitor over-blocks: it blocked 792 of 795 proposals, and authorized assembly under it was 0/50 in both wordings, so its 0/50 restricted result is not evidence of a useful safeguard.

Security reviewers will ask: *what if provenance is forged?* `README.md` says "Provenance is assumed trustworthy in the harness; resistance to forged metadata is not evaluated." For the global round, state this in the report's Limitations. For the LA round, raise it in the presentation rather than waiting for a question.

## 2. Pre-event talks and resources [summary]

These are listed on the Apart page but are not in `docs/hackathon/README.md` (consider moving them into its talks list rather than keeping a second schedule):

- Thu Nov 5: Adaption workshop (5:15 AM PT); John Kitaoka (MATS / UK AISI), "Open Problems in Securing Systems Against AI Agent Swarms"; Grant Fleming (AE Studio), "Novel Risks From Adversarially Optimized Agent Swarms".
- Fri Nov 6: Rowan Howard-Jones (Swarmchasers), "To Catch a Swarm"; Elias Stengel-Eskin (UT Austin), "The Emergence of Agent Languages".
- Recordings are on the Schedule tab and Discord.

## 3. Swarm Traces is a different channel from the board

Source: https://swarmtraces.org (fetched 2026-11-07), cited as `forman2026swarmtraces`; the article is dated Sept 25, 2026. Parts of this are [summary].

The Swarm Traces payloads come from the Hugging Face attack path, not from the Artifactory board. The link-shortener chains are confirmed in `docs/dev/datasets.md`; **[summary]** the screenshot-service rendering and httpbun paths are not.

- **[summary]** About 97% of payloads have no timestamp.
- Agent names: see `docs/research/metr-incident.md`, which already sources the 7,905 extracted names and warns not to mix that count with METR's roughly 1,200 board agents.
- Our reading, partly based on the [summary] timestamp figure: the data cannot serve as a source of coordination timelines. It is useful only as qualitative evidence that agents split work across many actors and many layers of encoding.

This qualifies the "no agent identities" note in `docs/dev/datasets.md`: name-like identifiers exist in the payloads, but agents renamed themselves often, so they do not identify agents reliably.

## 4. Adaption platform (sponsor; $500 credits per participant)

Source: https://docs.adaptionlabs.ai (read Nov 6). **[summary]** None of the specifics below (key prefix, URLs, install commands, row minimums, `estimate=True`) has been re-verified in this repo; check the docs before relying on them. These notes matter only if you use the credits.

- SDK: `pip install adaption`, with the key in `ADAPTION_API_KEY` (`pt_live_…`). Base URL: `https://api.prod.adaptionlabs.ai/api/v1`.
- Claude Code plugin:
  ```
  claude plugin marketplace add adaptionlabs/adaption-claude-plugin
  claude plugin install adaption@adaption
  ```
- Main products:
  - Adaptive Data improves datasets.
  - AutoScientist fine-tunes a model. SFT needs at least 1,000 rows; DPO needs at least 12,000.
  - Responses API offers hosted open models.
- Every spending call accepts `estimate=True`; `autoscientist.recommend_hyperparams` launches nothing.
- No obvious fit with the provenance study. Do not spend sprint time here unless a sponsor-usage story helps the LA presentation.

## 5. Exploratory side project (not part of the submission)

The session also built **SwarmWatch**, a Track 4 prototype that detects covert coordination from infrastructure logs only. It lives on its own branch, `explore/swarmwatch`, with unrelated history. It is deliberately **not** merged into `main`.

To try it:

```bash
git fetch origin explore/swarmwatch
git worktree add ../swarmwatch explore/swarmwatch
cd ../swarmwatch
uv run --no-project --with numpy --with scikit-learn --with matplotlib \
  python experiments/run_scripted.py --seeds 10 --out results/rerun
```

`--out results/rerun` keeps the committed outputs in `results/` intact. The run took about 40 seconds in the Cowork session and uses no model service. On a fresh machine, `uv` may need network access to download the dependencies first.

- Its results are synthetic and scripted: 10 seeds with adversary levels L0–L4. They have not been frozen or replicated.
- Do not put them in the report or the video. They are not part of this study's protocol, and mixing them in would undercut the repo's held-out discipline.
- If anything, cite the idea as future work. One candidate link is a monitor that sees board metadata rather than message content, which is relevant to the over-blocking finding.
