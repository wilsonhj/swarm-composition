# Implementation handoff for Claude Code agents

Start with [the implementation contract](sae-sender-implementation.md). It assigns
parallel work, defines the sender-only intervention, and sets the evidence gates
for Sunday's presentation. Read the [source audit](sae-source-audit.md) before
making research claims.

See [verification commands and limits](verification.md) for the tested replay,
the already collected provenance held-out run, and historical accounting gaps.

This handoff is independent of [PR #1](https://github.com/wilsonhj/swarm-composition/pull/1).
It adds a plan and audit tools; it does not implement or report an SAE experiment.

One concrete offline replay is already available. Run it from the repository root
against a clean worktree of the pinned snapshot (as CI does); later commits on `main`
changed `analyze.py`, so replaying the current checkout fails its pinned hash by design:

```bash
git worktree add --detach /tmp/swarm-v2-snapshot 59c8b7a84e88728d7fb67672dc57d2066bb3aff9
python3 docs/handoffs/tools/replay_v2.py --repo /tmp/swarm-v2-snapshot --out /tmp/swarm-v2-replay
```

Use Python 3.11 and a new output directory. The command verifies pinned inputs and
analysis sources, checks all 1,040 v2 rows against stored legacy scores, and writes
three separate analysis reports plus an audit summary and checksums. It uses no
network, API credentials, model downloads, or GPU. It preserves the original
results and keeps the Sonnet rerun separate. See the contract for its limits.

A second replay, `tools/replay_provenance.py`, rebuilds and rescores all 800
held-out task-provenance trials against a pinned snapshot; see
[verification](verification.md#provenance-held-out-replay).

CI also runs both replays against a separate checkout of the pinned artifact
snapshot and uploads `v2-artifact-replay` and `provenance-artifact-replay`. Future study-code changes therefore do
not silently change this historical audit's analysis source.

Templates to copy into the new study, then complete and validate:

- [Run manifest](templates/sae-run-manifest.template.json)
- [Claim ledger](templates/claim-ledger.template.csv)
- [Pinned v2 audit inputs](v2-inputs.json)

The manifest is deliberately incomplete and marked `template`. It is not run
evidence. The new study's validator must reject it until all required fields and
file hashes are resolved.
