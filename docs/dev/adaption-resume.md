# Continue the isolated Adaption pilot

The user authorized bounded retry and resume after pilot-02 stopped on HTTP 504.
This execution amendment does not change model IDs, seeds, task prompts, sampling,
the four trial cells, scorer or the 2-credit estimated total allowance. No frozen
study is modified. Both earlier attempts count against the allowance.

From `experiments/composition-gap`:

```bash
python3.11 adaption_resume.py > /tmp/adaption-resume-plan.json
python3.11 adaption_resume.py --execute --approve-plan REVIEWED_SHA256 \
  --out-dir results/adaption-cross-model-pilot-v1/pilot-03-resume
```

The runtime requires `ADAPTION_API_KEY`. The default source is pilot-02 and the
additional cost history is pilot-01. Planning is offline; the exact current
digest is required for execution. Repeating the execute command resumes the same
output directory, without appending duplicate valid trials or resending recorded
successful turns. A global process lock rejects concurrent continuations.

Five valid source trials are retained. The interrupted sixth trial replays its
two exact prior responses, checks the reconstructed request, and retries the
failed third worker request. Completed source files remain byte-for-byte intact.
Each successful response is durably journaled before further model calls. A crash
after a successful response but before a completed trial row is written recovers
that response from the journal. An incomplete final journal line is preserved
separately before repair; other corruption fails closed.

Retries are bounded to three total sends per logical turn, counting earlier
attempts. HTTP 502/503/504 and specifically classified transport failures are
eligible, with 5/15-second backoff. HTTP 4xx, malformed received JSON, incomplete
generation, model mismatch and missing usage are not automatically retried.
Terminal incomplete/empty generation is recorded as a failed trial, with its
remaining turns skipped; collection then continues with the other assigned trials.
Authentication, malformed JSON, model mismatch and unknown usage stop collection
for inspection. Completed failures are not resampled into successes on restart.
An unmatched durable attempt after interruption is treated as ambiguous, not free.

No exactly-once provider execution is claimed: a 504 or lost response can still
have generated output and incurred charges. Each ambiguous attempt retains its
own estimated reservation, including the historical 0.015711-credit reservation.
Known usage plus reservations across all models and earlier attempts is checked
before each new send. The 2-credit safeguard remains an estimate, not a provider
billing cap. The implementation stops before a new reservation would exceed it.

`calls.jsonl` contains only the new network attempts/results and logical-turn
identities. `completed_trials.jsonl` contains the newly completed trials, at most
19 for this continuation. `combined_trials.jsonl` is the explicit derived dataset:
the five retained source rows plus new completions, one row per assigned trial.
Copies of original rows retain original run/protocol/phase and row-hash lineage,
while the derived dataset uses a common new analysis identity. The repaired
failed trial also records replacement lineage; its original failure remains in
pilot-02. Original timing/model/call evidence on replayed turns is retained.

Analyze only the derived dataset for the complete pilot comparison:

```bash
python3.11 analyze.py results/adaption-cross-model-pilot-v1/pilot-03-resume/combined_trials.jsonl \
  --baseline local --md /tmp/adaption-completed-analysis.md
```

Do not combine it again with pilot-02, which would double-count retained trials.
Report segments, retries, unknown charges and failure replacements explicitly.
This is an exploratory continuation, not one uninterrupted or confirmatory run.

An execution-code amendment is explicit (`--amend-execution`), allowed only before
this continuation has written trial rows and only when scientific configuration,
sources, prices and total allowance are unchanged. The old manifest and both
plans are preserved; existing request journals and accumulated usage are reused.
