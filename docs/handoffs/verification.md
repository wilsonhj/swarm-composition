# Handoff verification record

Verified 7 November 2026. Existing inference artifacts were read and rescored;
no new hosted-model, local-model, training or GPU experiment was run.

## Available v2 audit

From this PR's exact commit, with the pinned raw/source files present:

```bash
python3 docs/handoffs/tools/replay_v2.py --out /tmp/swarm-v2-audit-1
python3 docs/handoffs/tools/replay_v2.py --out /tmp/swarm-v2-audit-2
diff -r /tmp/swarm-v2-audit-1 /tmp/swarm-v2-audit-2
cd /tmp/swarm-v2-audit-1
sha256sum -c SHA256SUMS
```

Use fresh output paths. The two generated bundles were byte-identical under the
same local environment (Python 3.12.14). The three group reports must also match
SHA256 values pinned in `v2-inputs.json`; they matched under CPython 3.11, 3.12
and 3.13 on 7 November 2026. `audit.json` (and so `SHA256SUMS`) includes
environment and checkout metadata and is not pinned. The audit status is
`artifact_replay_passed` only for a clean checkout of the pinned snapshot commit
(as in CI); otherwise it is `artifact_replay_passed_noncanonical_checkout`. Use
the former for final presentation evidence.

Observed: **1,040 rows, 7,670 logged logical calls, 1,040 stored legacy score
triples reproduced**, no failures in these nine v2 runs. Raw files, manifests,
and the three analysis sources are checked against 21 pinned SHA256 values.
Original and rerun Sonnet reports are separate.

Negative-path checks also passed:

- Running against an existing output directory returned exit status 1.
- Copying the allowlisted inputs to a temporary fixture and appending a newline
  to one raw file returned exit status 1 with `SHA256 mismatch`, before producing
  an output directory. Even a score-neutral raw-file change is detected.
- A run that fails after hashing (for example, a group report differing from its
  pinned hash) returned exit status 1 and left no output directory.
- An untracked `random.py` placed beside the analysis sources was not imported:
  the analyzer runs from a temporary copy of the hash-verified sources only.

These checks establish input integrity and deterministic local replay. They do
not recover unlogged historical retries or promise future hosted-model behavior.
Archived reports are preserved; generated reports use the pinned analysis source.

## Provenance held-out artifact check

The inspected PR #1 snapshot is `a5258393ac6baf718b3a2b0042dae195b90f90bd`.
Preparing a separate checkout may need network access once:

```bash
git fetch origin a5258393ac6baf718b3a2b0042dae195b90f90bd
git worktree add --detach /tmp/swarm-provenance-audit a5258393ac6baf718b3a2b0042dae195b90f90bd
```

Once prepared, the following analysis uses only the standard library and archived
data; it requires no credentials or network:

```bash
cd /tmp/swarm-provenance-audit/experiments/composition-gap
python3 analyze.py results/task-provenance/heldout-haiku.jsonl --baseline local --md /tmp/provenance-replay.md
```

Independent checks on that snapshot found:

| Field | Verified value |
|---|---|
| Run ID | `4c134cfd-0a87-49f2-ba16-a4cba153a701` |
| Collection commit | `435d20d4d0d8e7bf24a391d077649b98e6d526ae`, manifest says clean |
| Raw SHA256 | `066b505a69e545f682562117a0ae0c43aacce37014b80effb044996e10e44933` |
| Protocol SHA256 | `5a8659fea984ee3203f380476e06cdc72829e4b574e88edbbcfbda5800ead978` |
| Trials | 800; four conditions × two authorizations × two wordings × 50 seeds |
| Failure | One worker turn, seed 3010, authorized/paraphrase/provenance trial |
| Calls | 4,795 raw turn records, of which one failed; manifest backend count 4,794 |
| Stored scores | `assembled`, `recoverable`, `identified_parts`, `exposed_parts`, `assembled_exact` reproduce in all 800 rows |
| Model identity | Manifest resolved-model list contains `claude-haiku-5-5`; failed worker turn has no served ID |

The fresh report reproduces the archived estimates/intervals and adds full paired
tables plus interpretation notes from newer analysis code. Its Markdown therefore
differs from the archived report. This is why collection and analysis commits must
be recorded separately. The missing failed-call identity and historical counter
difference remain disclosed gaps. They must not be silently repaired in raw data.

The current one-command v2 tool does **not** package this provenance check.
Agent A is assigned to add manifest validation, score/paired-table checks and
claim-ledger export for these provenance artifacts. The command above already
recreates their analysis; a complete presentation bundle still needs that work.

## Repository and document checks

- Base-main suite: **124 tests passed**, including the installed Anthropic SDK's
  fake-localhost API test. The initial sandbox denied binding the local test
  server; the same suite passed when run with local-socket permission. No remote
  model endpoint was contacted.
- Mock v1 and v2 smoke runs passed; outputs went to temporary paths.
- `git diff --check`, replay script compilation, local Markdown links, cited
  bibliography keys, duplicate bibliography detection, JSON parsing, and CSV
  header validation passed. The bibliography contains 49 unique keys after the
  additions; existing entries were preserved.

The suite command used the cached offline environment:

```bash
cd experiments/composition-gap
UV_CACHE_DIR=/tmp/swarm-uv-cache UV_OFFLINE=1 uv run --no-project --with pytest==9.2.0 --with 'anthropic>=0.40,<3' pytest -q
```

The cache path is specific to this verification environment. On a new machine,
install dependencies before disabling network. Final PR checks and their commit
are recorded by GitHub Actions. GPU routing/compatibility/effectiveness remain
future acceptance gates, not passes implied by these CPU checks.

CI now checks the v2 replay against a detached worktree at the immutable main
snapshot and uploads the generated audit packet. This tests the new replay tool
on Python 3.11 while preserving historical analysis semantics. The artifact
snapshot's commit is intentionally distinct from the handoff/tool PR commit.
