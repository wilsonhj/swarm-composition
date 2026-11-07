# Handoff verification record

Verified 7 November 2026. Existing inference artifacts were read and rescored;
no new hosted-model, local-model, training or GPU experiment was run.

## Available v2 audit

From the repository root, against a clean worktree of the pinned snapshot (later
commits on `main` changed `analyze.py`, so the current checkout fails its pinned hash):

```bash
git worktree add --detach /tmp/swarm-v2-snapshot 59c8b7a84e88728d7fb67672dc57d2066bb3aff9
python3 docs/handoffs/tools/replay_v2.py --repo /tmp/swarm-v2-snapshot --out /tmp/swarm-v2-audit-1
python3 docs/handoffs/tools/replay_v2.py --repo /tmp/swarm-v2-snapshot --out /tmp/swarm-v2-audit-2
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

## Provenance held-out replay

From the repository root, against a clean worktree of the merged PR #1 snapshot
(the replay also reads the freeze commit from git history, so use a full clone):

```bash
git worktree add --detach /tmp/swarm-provenance-snapshot e056c88a9a75efb23d7e147e7b366cadc81fc01b
python3 docs/handoffs/tools/replay_provenance.py --repo /tmp/swarm-provenance-snapshot --out /tmp/swarm-provenance-replay-1
python3 docs/handoffs/tools/replay_provenance.py --repo /tmp/swarm-provenance-snapshot --out /tmp/swarm-provenance-replay-2
diff -r /tmp/swarm-provenance-replay-1 /tmp/swarm-provenance-replay-2
cd /tmp/swarm-provenance-replay-1 && sha256sum -c SHA256SUMS
```

Observed on 7 November 2026 under CPython 3.11.16 and 3.12.14: **800 trials (16
cells × seeds 3000–3049), 4,795 logged turns, all 800 trials rebuilt from their
logged replies and rescored, 0 malformed monitor verdicts, 0 non-protocol
replies.** Output is `provenance_replay_passed` only for a clean checkout of the
snapshot; otherwise `provenance_replay_passed_noncanonical_checkout`.

The replay checks 9 files in the checkout and 4 files at freeze commit `435d20d`
against pinned SHA256 values ([`provenance-inputs.json`](provenance-inputs.json))
and asserts every expected count listed there:

| Field | Verified value |
|---|---|
| Run ID | `4c134cfd-0a87-49f2-ba16-a4cba153a701` |
| Collection commit | `435d20d4d0d8e7bf24a391d077649b98e6d526ae`, clean; ancestor of the snapshot |
| Raw SHA256 | `066b505a69e545f682562117a0ae0c43aacce37014b80effb044996e10e44933` |
| Protocol SHA256 | `5a8659fea984ee3203f380476e06cdc72829e4b574e88edbbcfbda5800ead978` (equals manifest `protocol_hash` and the file at the freeze commit) |
| Prompts | manifest `prompt_hash` recomputed from `provenance.py` templates |
| Served model | `claude-haiku-5-5` on all 4,794 successful turns; the failed turn records none |
| Failure | 1 trial: provenance / authorized / paraphrase, seed 3010, worker1; excluded (valid n 49); all-trial bounds assembled 66–68%, recoverable 94–96% |
| Calls | 4,795 logged turns = manifest `calls` 4,794 + `errors` 1 |
| Monitor | 795 proposals: 792 BLOCK, 3 ALLOW (authorized/paraphrase), 0 malformed |
| Rebuild | every trial re-run through `provenance.run_trial` from its logged replies equals the stored row (except per-turn `ms`, the later `fail_reason` turn field and run metadata); all 15 `score_row` fields reproduce |
| Cells and contrasts | all 16 cell tallies and the four provenance-vs-local contrasts in `provenance-heldout.md` |

**Call counter.** In the collection harness, `ClaudeCode` incremented `calls` only
on a successful logical call; a call that exhausted its three attempts incremented
`errors` instead. Logged turns therefore equal `calls + errors`. Transport retries
inside a call, and their cost and served model, were not recorded (changed after
the freeze in `57d13c3`). This is a disclosed gap, not a repair.

**Committed analysis.** `heldout-haiku.jsonl.analysis.md` was generated by the
analyzer at the freeze commit. The replay regenerates it byte-identically from
those hash-pinned sources (`analysis_collection.md`). The snapshot analyzer's
report (`analysis_snapshot.md`, also pinned) adds two paired-count columns and a
longer contrast note; the replay asserts that these are the only differences.
Both report hashes match under CPython 3.11 and 3.12.

Negative-path checks (`python -m unittest discover -s docs/handoffs/tests`)
passed: a modified raw file fails its hash before any output is created; a score
tampered with in a raw row with a re-pinned hash fails the rebuild; existing or
in-checkout `--out` paths are refused; a failure after hashing (a wrong pinned
report hash) leaves no output or partial directory; an untracked `random.py` or
`json.py` beside the sources is not imported.

These checks establish integrity and deterministic local replay of one archived
run. They do not recover unlogged retries or the failed turn's model, verify the
reported cost, or say anything about future hosted-model behaviour.

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
