# Cowork research session notes (Nov 6–7, 2026)

These notes are a delta: they record only what a separate Claude Cowork research session found that this repo does not already contain. The METR incident, dataset access, deadlines and rules are already covered in more detail (and more carefully sourced) in `docs/research/metr-incident.md`, `docs/dev/datasets.md` and `docs/hackathon/`. Where the two disagree, trust those files.

Verification status: everything below came from a web-fetch subagent. Items marked **[summary]** came from the tool's model-written summary of the part of the page it could not show verbatim. Re-fetch them before citing in the report (repo rule: cite only fetched sources).

## 1. Global judge panel (Apart page) [summary]

Source: https://apartresearch.com/sprints/swarm-alignment-2026 (fetched 2026-11-07). The roster sat beyond the verbatim cutoff, so names and affiliations are unverified.

The panel leans heavily toward security, identity and production engineering:

| Background | Judges |
|---|---|
| Red teaming and security | Mateusz Dziemian (Gray Swan), Reworr (UK AISI red team via MATS), Nirav Patel (Okta), Casey Barkan (RAND) |
| Large-company engineering | Microsoft, Meta, Amazon (×3), Salesforce (×2), Uber, PayPal, Snowflake, Intuit, Box, Pega, Jane Street |
| Research | Dane Malenfant (Mila), Amelie Knecht (Stuttgart / MATS), Jady Pamella (Aarhus), Andrey Anurin and Kunvar Thaman (Apart), George Ingebretsen (AI Village) |

About 50 judges are listed in total. Each scores Impact & Innovation, Execution and Presentation on a 1–5 scale, and scores are not shared.

**What this implies for framing.** The provenance result reads naturally as an access-control finding for this audience:

- A context-blind restriction is bypassed by decomposition: 45/50 restricted recoverability under `local`.
- Propagating trusted task metadata fixes it without a utility tax: 0/50 restricted, and authorized assembly rises from 15/50 to 33/49.
- It beats a naive keyword gate in both directions.
- An LLM monitor over-blocks: 792 of 795 proposals blocked.

Security judges will immediately ask: *what if provenance is forged?* `README.md` already lists this as out of scope. Name it in the first minute of Q&A rather than waiting for the question.

## 2. Pre-event talks and resources [summary]

These are listed on the Apart page but are not in `docs/hackathon/README.md`:

- Thu Nov 5: Adaption workshop (5:15 AM PT); John Kitaoka (MATS / UK AISI), "Open Problems in Securing Systems Against AI Agent Swarms"; Grant Fleming (AE Studio), "Novel Risks From Adversarially Optimized Agent Swarms".
- Fri Nov 6: Rowan Howard-Jones (Swarmchasers), "To Catch a Swarm"; Elias Stengel-Eskin (UT Austin), "The Emergence of Agent Languages".
- Recordings are on the Schedule tab and Discord.

## 3. Swarm Traces is a different channel from the board

Source: https://swarmtraces.org (fetched 2026-11-07); the article is dated Sept 25, 2026. Parts of this are [summary].

The Swarm Traces payloads come from the Hugging Face attack path: link-shortener URL chains, screenshot-service rendering and httpbun. They do **not** come from the Artifactory board.

- **[summary]** About 97% of payloads have no timestamp.
- **[summary]** There are 7,905 unique agent names for roughly 1,200 agents.
- The data cannot serve as a source of coordination timelines. It is useful only as qualitative evidence that agents split work across many actors and many layers of encoding.

This complements the "agent IDs unknown" note in `docs/dev/datasets.md`.

## 4. Adaption platform (sponsor; $500 credits per participant)

Source: https://docs.adaptionlabs.ai (read Nov 6). These notes matter only if you use the credits.

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

The session also built **SwarmWatch**, a Track 4 prototype that detects covert coordination from infrastructure logs only. It ships separately as `swarmwatch.zip`, or on branch `explore/swarmwatch` if that branch was imported.

- Its results are synthetic and scripted: 10 seeds with adversary levels L0–L4. They have not been frozen or replicated.
- Do not put them in the report or the video. They are not part of this study's protocol, and mixing them in would undercut the repo's held-out discipline.
- If anything, cite the idea as future work. One candidate link is a monitor that sees board metadata rather than message content, which is relevant to the over-blocking finding.
