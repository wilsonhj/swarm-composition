# Recorded development and execution timeline

Checked 7 November 2026 against git history, committed run manifests, and the official event schedule. This record distinguishes **before this amendment** from **before the sprint**. The former does not imply the latter.

The [official LA schedule](https://aialignmentfoundation.org/hackathons/swarm-alignment-2026) places kickoff at 13:30 Pacific on Friday 6 November, and the hacking session at 15:30. Pacific time was PST (UTC−08:00). The [Apart guidelines](https://apartresearch.com/sprints/swarm-alignment-2026#guidelines) require genuinely pre-sprint work to be identified in the README and report; they do not classify earlier work within the same weekend as pre-sprint.

| Recorded event | UTC | Pacific (PST) | Source |
|---|---|---|---|
| LA kickoff | Nov 6, 21:30 | Nov 6, 13:30 | Official LA schedule |
| LA hacking session begins | Nov 6, 23:30 | Nov 6, 15:30 | Official LA schedule |
| Initial repository scaffold | Nov 7, 01:24:25 | Nov 6, 17:24:25 | [commit e227aa9](https://github.com/wilsonhj/swarm-composition/commit/e227aa9) |
| v2 implementation | Nov 7, 02:29:30 | Nov 6, 18:29:30 | [commit 4c89f80](https://github.com/wilsonhj/swarm-composition/commit/4c89f80) |
| First Haiku v2 cell starts | Nov 7, 02:49:12 | Nov 6, 18:49:12 | [manifest](../../experiments/composition-gap/results/v2/2026-11-06_55325c9a_claude-haiku-5-5_v2_none_neutral.jsonl.manifest.json) |
| First Sonnet v2 cell starts | Nov 7, 04:31:21 | Nov 6, 20:31:21 | [manifest](../../experiments/composition-gap/results/v2/2026-11-06_9c37b82a_claude-sonnet-5-5_v2_none_neutral.jsonl.manifest.json) |
| Provenance development pilot starts | Nov 7, 05:31:14 | Nov 6, 21:31:14 | [manifest](../../experiments/composition-gap/results/task-provenance/pilot-haiku-2026-11-07.jsonl.manifest.json) |
| Provenance protocol frozen after development | Nov 7, 06:00:41 | Nov 6, 22:00:41 | [commit 435d20d](https://github.com/wilsonhj/swarm-composition/commit/435d20d) |

Commit timestamps record repository history, not independent proof of when each line was authored. Run timestamps are the recorded execution times; they do not independently certify the host clock. Earlier pilot files with incomplete provenance need item-specific confirmation. Do not infer their authoring/execution dates from a later commit or label all pilots pre-event.

## Suggested report disclosure

> Repository history records scaffolding and v2 implementation on Friday 6 November 2026 after the published LA kickoff. The v2 run manifests record execution during the sprint. The provenance study is a later, separately versioned development study. These records do not establish the authoring date of every asset; any genuinely pre-sprint code or results must be disclosed individually. Earlier pilots were used for design selection and are exploratory, irrespective of their eligibility classification.

Before submission, the team must confirm any assets created before the sprint. Do not substitute either an unverified “none existed” statement or an unsupported blanket “all existing work was pre-sprint” statement. Keep per-cell source commits and manifest timestamps: the v2 cells were not all executed at one source commit.

## Study boundaries

| Work | Evidence and status | Submission treatment |
|---|---|---|
| v1/v2 context-composition study | Completed runs; v2 Haiku/Sonnet data and same-task rerun | Report measured outcomes, model-routing caveat, independent task counts and contrast definitions |
| task-provenance-v1 | Development pilot on 2000–2019; protocol frozen at 435d20d; no held-out outcomes are added by this amendment | Explicitly label development results; do not count them as held-out evidence |
| SAE sender-intervention study | Research proposal; no installed local backend verified | Future work, without results, performance claims or a verified GPU budget |
