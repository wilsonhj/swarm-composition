# Adaption inference: separate exploratory pilot

This branch was integrated with main at `3cc02e4` (7 November 2026), including
PR #10's environment-variable documentation and PR #9's correction of the
Adaption estimate claim. Recent merges improved
the report, CI, research audit, guide and submission instructions; they did not
add Adaption inference. The completed provenance held-out run is already present.
OpenRouter already offers a cross-model route; this addition instead makes the
user's reported 1,000 Adaption credits usable for an optional, separate pilot.

Flow: CLI configuration → offline plan → explicit digest approval → model-availability
GET → isolated Responses POST → per-turn audit / scores → JSONL and manifest →
existing offline analyzer. There is no browser or Vercel deployment in this story.

## Prepare without spending

From `experiments/composition-gap`, with Python 3.11:

```bash
python3.11 adaption_pilot.py > /tmp/adaption-plan.json
python3.11 adaption_pilot.py --mode mock --out-dir /tmp/adaption-mock-review
python3.11 analyze.py /tmp/adaption-mock-review/trials.jsonl --baseline local --md /tmp/adaption-mock-analysis.md
```

Plan and mock require neither credentials nor network. No `.env` file is read.
The mock is scripted plumbing evidence, not observed model behavior. The checked-in
[configuration](../../experiments/composition-gap/adaption-pilot.json) and
[new pilot protocol](../protocols/adaption-cross-model-pilot-v1.md) define 24 trials
and 120 logical actor calls. No frozen prompt, protocol, result or analyzer is
edited. Study/design/run/backend/model/prompt/protocol identities keep the new
data separate in `analyze.py`.

## Estimate before approval

The [published hosted rates](https://docs.adaptionlabs.ai/inference-stacks/models/)
are credits per million input/output tokens [adaption2026models]. This configuration
uses standard uncached rates, with no caching discount:

| Model | Input / output rate | Calls | 500 input + 4,096 output/call | 2,500 input + 4,096 output/call |
|---|---|---:|---:|---:|
| Gemma 4 31B | 0.09 / 0.34 | 60 | 0.0862584 | 0.0970584 |
| Qwen 3.5 397B | 0.55 / 3.50 | 60 | 0.8766600 | 0.9426600 |
| Total | credits | 120 | **0.9629184** | **1.0397184** |

These are estimates assuming every call generates the full output allowance.
Actual input varies with worker replies and assembler boards. The byte-count
input guard is a conservative engineering heuristic, not a tokenizer theorem.
Reasoning accounting, ambiguous failed requests, provider prices and account
terms can change charges. `max_credits: 2.0` stops sending when local reservations
would exceed it; it does not guarantee a provider billing cap. Unknown usage or
ambiguous transport failure keeps the reservation and stops further sending.
`cost` remains null rather than labeling credits as dollars.

Responses has no estimate endpoint. The script's plan is local arithmetic,
not a provider quote. Model availability is key-specific. The user's balance
has not been independently verified. Review account rates and credit restrictions
before accepting a live plan [adaption2026models, adaption2026responses].

## Live execution after approval only

Set `ADAPTION_API_KEY` securely in the process environment. Do not put its value
in a command saved to the repository. No new key is created by this tooling.
Use `approval_sha256` from the reviewed plan:

```bash
python3.11 adaption_pilot.py --mode execute \
  --approve-plan REVIEWED_PLAN_SHA256 \
  --out-dir results/adaption-cross-model-pilot-v1/pilot-01
```

Without the exact current digest, the runner exits before key lookup or network.
The digest pins configuration and runner/backend/harness/scoring source hashes.
It must be regenerated after edits. Approval does not imply a clean committed
protocol freeze; commit and record the implementation before a future scientific
collection. Output creation is exclusive; no append/rerun over existing files.

Execution first checks the hosted model IDs using a read-only authenticated GET;
if either is unavailable, no inference is sent [adaption2026modellist]. HTTP POST
uses the fixed official Responses endpoint, with no implicit retries, memory,
tools, background execution or stored history. Backend failure returns a failed
turn through the existing `Backend`/`Turns` interface, never a scored success.
Reasoning items remain in the audit but only assistant text reaches the parser.
Mismatched served model, missing usage, tool calls, partial output and refusal
content items stop the pilot for review [adaption2026responses].

Outputs are `trials.jsonl` and `manifest.json`, plus an append-only `calls.jsonl`
for live runs. Attempt/result events are flushed and synced per call, including
partial trials interrupted before a result row can be written. Each live turn retains its request
(without authorization headers), raw response, usage, served model, status,
failure classification and timing. Credits are recomputed at the configured
uncached rates, not claimed as billing data. After successful collection:

```bash
python3.11 analyze.py results/adaption-cross-model-pilot-v1/pilot-01/trials.jsonl \
  --baseline local --md /tmp/adaption-pilot-analysis.md
```

## Verification and collection boundaries

Tests use fake/local transport only. They cover the offline plan, approval rejection,
mock run and analyzer, plus malformed/failed/incomplete Responses, usage accounting,
no implicit backend retries, combined-model budget, and frozen-output protection.
The separately authorized [completed pilot](../findings/adaption-cross-model-pilot.md)
records real hosted responses, failures, usage and estimated charges. Final billing
and the account balance remain unverified. Preparing and verifying the adapter
uses no model credits; live execution is a separate action.
