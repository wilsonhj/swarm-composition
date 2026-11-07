# Anthropic API (`claude` backend), short reference

Fetched **2026-11-06**. The team mostly uses OpenRouter and Claude Code, so this is a minimal sheet.

Sources:
- Get started (curl and SDK examples): https://platform.claude.com/docs/en/get-started
- Models overview (IDs, prices): https://platform.claude.com/docs/en/about-claude/models/overview (redirects to https://platform.claude.com/docs/en/models/overview)
- Messages API reference: https://platform.claude.com/docs/en/api/messages
- Pricing: https://platform.claude.com/docs/en/about-claude/pricing (linked from the models page; not fetched)
- Model IDs and versioning: https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions (linked; not fetched)

## Messages API basics

`POST https://api.anthropic.com/v1/messages` (from the get-started page):

```bash
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2026-10-21" \
  -d '{
    "model": "claude-haiku-5-5",
    "max_tokens": 200,
    "system": "<system prompt>",
    "messages": [{"role": "user", "content": "<user prompt>"}]
  }'
```

- The `anthropic-version` value `2026-10-21` is what the quickstart shows today. Older code often sends an earlier date; check the SDK default rather than hard-coding if using the Python SDK.
- Required body fields (reference page): `model`, `max_tokens`, `messages`. The reference page excerpt did not label them "required" explicitly, but they are the fields without an optional marker.
- The top-level `system` field for the system prompt is **not shown** in the fetched excerpts. It is standard in the Messages API, but treat it as **unverified** until you check the reference.
- Response (quickstart example): `id`, `type: "message"`, `role`, `content` (list of blocks, text in `{"type":"text","text":...}`), `stop_reason`, `stop_sequence`, `stop_details`, `usage: {input_tokens, output_tokens}`, `model`.
- The Messages API returns **tokens, not dollars**. Compute cost yourself from `usage` and the price table below.

Python SDK (from the quickstart): `pip install anthropic`, then `anthropic.Anthropic().messages.create(model=..., max_tokens=..., messages=[...])`; the client reads `ANTHROPIC_API_KEY` from the environment.

Auth note: a key set as `ANTHROPIC_API_KEY` is also picked up by the Claude Code CLI in `-p` mode (see `claude-code-cli.md`), which is why the Claude Code backend strips it.

## Current model IDs

From the models overview ("Claude API ID" row; each ID is a pinned snapshot, dateless):

| Model | API ID | Input $/MTok | Output $/MTok | Context / max output | Retirement (not sooner than) |
|---|---|---|---|---|---|
| Claude Haiku 5.5 | `claude-haiku-5-5` | from 0.10 | from 0.50 | 1M / 128K | 2027-10-07 |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 2 | 10 | 1M / 128K | 2027-09-28 |
| Claude Opus 5.5 | `claude-opus-5-5` | 4 | 20 | 1M / 128K | 2027-09-22 |
| Claude Fable 5.1 (extra) | `claude-fable-5-1` | 10 | 50 | 1M / 128K | 2027-09-01 |

All three requested IDs (`claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`) are confirmed. On OpenRouter the same models are `anthropic/claude-haiku-5.5` and so on (dots, not dashes). Prices match the OpenRouter list, so there is no markup on these three.

Thinking (relevant to cost): all four use adaptive thinking; Haiku/Sonnet default effort is `medium`/`high` as listed on the page (Haiku `medium`, Sonnet `high`, Opus `medium`, Fable `high`). The page says the Models API reports `thinking.types.disabled.supported = false` for Sonnet 5.5, so a plain request will think by default and bill the thinking as output. Whether Haiku 5.5 and Opus 5.5 accept `thinking: {type: "disabled"}`, and whether the `effort` parameter is set via `output_config` or elsewhere, was **not verified**: see https://platform.claude.com/docs/en/build-with-claude/effort and https://platform.claude.com/docs/en/build-with-claude/thinking.

Legacy models still available (per the page): Fable 5, Opus 5, Opus 4.8/4.7/4.6/4.5, Sonnet 5, Sonnet 4.6, Haiku 4.5.

Batch API: 50% off (models page). Not used by the harness.

## Rate limits and errors

Not fetched. See https://platform.claude.com/docs/en/api/rate-limits (linked from the Claude Code costs page). Marked **unverified** here.
