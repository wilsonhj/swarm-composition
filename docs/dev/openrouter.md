# OpenRouter backend reference

Facts below were fetched on **2026-11-06** from the pages linked in each section. Anything marked **unverified** was not confirmed in a fetched source. No authenticated API calls were made while writing this (the model list is a public endpoint).

Sources:
- API overview: https://openrouter.ai/docs/api-reference/overview
- Usage accounting: https://openrouter.ai/docs/guides/guides/usage-accounting
- Limits / key info: https://openrouter.ai/docs/api-reference/limits
- Errors: https://openrouter.ai/docs/api-reference/errors
- Credits: https://openrouter.ai/docs/api-reference/get-credits
- Reasoning tokens: https://openrouter.ai/docs/guides/best-practices/reasoning-tokens
- Model list (public JSON): https://openrouter.ai/api/v1/models

## Auth, base URL, endpoint

- Base URL: `https://openrouter.ai/api/v1` (the docs' examples call `https://openrouter.ai/api/v1/chat/completions`).
- Auth header: `Authorization: Bearer <OPENROUTER_API_KEY>`.
- Harness env: `OPENROUTER_API_KEY` (key) and `OPENROUTER_BUDGET_USD=250`. The budget variable is a harness-side convention. OpenRouter does not read it; the harness has to sum `usage.cost` itself and stop (see Budget).

## Attribution headers (optional)

| Header | Meaning (per overview page) |
|---|---|
| `HTTP-Referer` | Identifies your app on openrouter.ai |
| `X-OpenRouter-Title` | Sets/modifies your app title. The page says `X-Title` is also accepted. |
| `X-OpenRouter-Categories` | Assigns marketplace categories |

Suggested: `HTTP-Referer: https://github.com/<org>/swarm-composition`, `X-Title: swarm-composition composition-gap` (the exact values are our choice; the repo URL is a placeholder).

## Chat completions: request

`POST /api/v1/chat/completions`, JSON body. From the overview page:

- Needs `messages` (array of `{role, content}`) or `prompt` (string).
- `model`: optional (falls back to the account default). Always pass it explicitly, with the organisation prefix, for example `anthropic/claude-haiku-5.5`.
- Other documented fields: `stream`, `temperature`, `max_tokens`, `tools`, `tool_choice`, `response_format`, `plugins`, `provider`, `models`, `user`.

Minimal body for the harness (system prompt + user prompt, one-line reply):

```json
{
  "model": "anthropic/claude-haiku-5.5",
  "messages": [
    {"role": "system", "content": "<60-90 word system prompt>"},
    {"role": "user",   "content": "<40-150 word user prompt>"}
  ],
  "max_tokens": 120,
  "temperature": 1.0
}
```

`reasoning`, `seed` and the other optional fields are **not** in the minimal body above. See "Reasoning tokens" before choosing `max_tokens`.

## Chat completions: response

Top-level fields (overview page): `id`, `choices`, `created`, `model`, `object`, `system_fingerprint` (optional), `usage`.

- `choices` is always an array. Each choice has `finish_reason`, `native_finish_reason` and `message` (non-streaming) or `delta` (streaming).
- Normalised `finish_reason`: `tool_calls`, `stop`, `length`, `content_filter`, `error`.
- Reply text: `choices[0].message.content`.
- `usage`: `prompt_tokens`, `completion_tokens`, `total_tokens`, `cost`.

## Per-request cost (usage accounting)

From the usage-accounting page:

- **No request flag is needed.** `usage: {include: true}` and `stream_options: {include_usage: true}` are described as deprecated and have no effect.
- `usage.cost` = total amount charged to your account, in credits.
- `usage.cost_details.upstream_inference_cost` = what the upstream provider charged. Per that page it is only populated for BYOK requests; otherwise 0 or null. **Use `usage.cost`.**
- Chat-completions split fields: `upstream_inference_prompt_cost`, `upstream_inference_completions_cost`.
- Fetch cost later by saving the response `id` and calling the `/generation` endpoint ("Get a Generation" in the API reference). The exact query parameter name was **not** confirmed. Check that reference page before using it.
- Page example shows `"cost": 0.95` next to `prompt_tokens: 194`. The page does not state the unit of the example, so do not read it as dollars. Treat 1 credit = 1 USD as **unverified** and confirm with a single cheap call against the dashboard before wiring up the budget guard.

Harness pattern: after each call, `spent += resp["usage"]["cost"]`; persist `spent` to the run log; abort when `spent >= float(os.environ["OPENROUTER_BUDGET_USD"])`. Also log `usage.completion_tokens_details.reasoning_tokens` (see below).

## Reasoning tokens (cost risk)

From the reasoning page:

- The request accepts a `reasoning` object: `effort` (`high`/`medium`/`low`, and `"none"` disables reasoning), `max_tokens` (exact reasoning budget, for models that support token allocation, e.g. Anthropic and Gemini thinking models), `enabled`, `exclude`. Use either `effort` or `max_tokens`, not both.
- For models marked `mandatory`, reasoning cannot be disabled and `effort: "none"` is rejected.
- **Reasoning tokens are billed as output tokens**, and `exclude` only hides them. They still count toward `max_tokens`, so a small `max_tokens` can yield an empty visible answer.
- Read them from `usage.completion_tokens_details.reasoning_tokens` (Chat Completions).
- In the public model list, nearly every model below carries `reasoning` / `include_reasoning` in `supported_parameters` (the Llama 4 and Llama 3.3 entries do not). Which of them are `mandatory` was **not** determined. Probe each model once (one call, read `reasoning_tokens`) before a full run.
- Anthropic's own models page says Sonnet 5.5 rejects `thinking: {type: "disabled"}` (see `anthropic-api.md`), so expect hidden thinking tokens on 5.5-generation Claude models. Whether OpenRouter applies the same rule to `reasoning.effort = "none"` is **unverified**.

## Remaining credit / key limit

From the limits page:

- `GET https://openrouter.ai/api/v1/key` with your API key. Fields under `data`: `label`, `limit` (null = unlimited), `limit_reset`, `limit_remaining` (null = unlimited), `include_byok_in_limit`, `budgets` (list in enforcement order), `effective_budget` (the one that blocks first; has `limit_usd`, `spend_usd`, `remaining_usd`, `reset_interval`, `resets_at`, `include_byok`), `usage`, `usage_daily`, `usage_weekly`, `usage_monthly`, `is_free_tier`, `free_model_daily_requests`. `rate_limit` is deprecated.
- `GET https://openrouter.ai/api/v1/credits` returns `data.total_credits` (bought) and `data.total_usage` (spent), but per the credits page it **requires a management key**; ordinary keys get 403.
- So for "how much is left", use `/key` (`limit_remaining` if the key has a cap, otherwise `usage`) from the harness, and `/credits` only with a management key. Neither call was made here (no key used).

## Rate limits

- Free models (IDs ending `:free`): 20 requests/min; 50/day if under 10 credits bought all time, 1000/day otherwise (the page's own text for the threshold was partly garbled; treat the precise threshold as approximate).
- Paid models: the page says there is **no platform-level request cap** for paid variants. Upstream providers can still rate-limit (429).
- Do not use `:free` models for experiments: the quota is tiny and the pool is not stable.

## Errors and retries

Error body (errors page): `{"error": {"code": <int>, "message": <str>, "metadata": {...}?}}`. The HTTP status matches `error.code` for request errors, but errors raised **mid-generation can arrive with HTTP 200**, so check for an `error` field even on 200.

| Code | Meaning | What to do |
|---|---|---|
| 400 | Bad request / invalid params | Fix; do not retry unchanged |
| 401 | Bad or disabled key | Stop the run |
| 402 | Insufficient credits (or key cap) | See below; stop unless `limit_source` is the in-flight budget |
| 403 | Forbidden: guardrail, moderation, spent budget | Change input, or wait for `metadata.resets_at` |
| 408 | Timeout | Retry with backoff (the page gives no specific guidance; this is our choice) |
| 429 | Rate limited | Wait `Retry-After`, retry |
| 502 | Model down or invalid response | Retry with backoff; consider another provider/model |
| 503 | No provider meets routing requirements | Wait `Retry-After` if present, retry |

402 detail (limits page): inspect `error.metadata.limit_source`:
- `openrouter_in_flight_budget`: transient, wait the `Retry-After` header, then retry. (`reason` `weight_exceeds_budget` means retrying will not help.)
- `openrouter_key_limit`: key cap used up. Raise it or wait for the reset.
- `openrouter_credits`: balance cannot cover the request. Add credits, or lower `max_tokens` / prompt size.

The official SDKs back off on 429/503 automatically but **do not** retry 402. If the harness uses raw `requests`/`httpx`, implement: retry 429/502/503/408 with exponential backoff plus jitter (cap ~5 attempts, honour `Retry-After`), treat 402 per `limit_source`, fail fast on 400/401/403. Count only successful responses toward `spent`.

## Models for cross-model comparison

Source: `GET https://openrouter.ai/api/v1/models` (public, unauthenticated), fetched **2026-11-06**. Prices are the `pricing.prompt` / `pricing.completion` fields, multiplied by 1,000,000, in USD per million tokens (USD unit is the API's convention. See the credit-unit caveat above). Slugs are exact `id` values.

Tier labels ("cheap", "frontier") are ours, based on price and on the model description text in the list. They are not an OpenRouter field.

| Family | Tier | Slug | Input $/M | Output $/M | Notes |
|---|---|---|---|---|---|
| Anthropic | cheap | `anthropic/claude-haiku-5.5` | 0.10 | 0.50 | 1M ctx. Higher rate above 100k prompt tokens (irrelevant here) |
| Anthropic | mid | `anthropic/claude-sonnet-5.5` | 2.00 | 10.00 | |
| Anthropic | frontier | `anthropic/claude-opus-5.5` | 4.00 | 20.00 | |
| Anthropic | top (extra) | `anthropic/claude-fable-5.1` | 10.00 | 50.00 | Fable line; listed on Anthropic's models page as the top tier |
| OpenAI | cheap | `openai/gpt-6-luna` | 0.10 | 0.50 | Described as fast, cost-efficient, below GPT-6 Sol |
| OpenAI | mid | `openai/gpt-6.1-terra` | 1.00 | 5.00 | Described as mid-tier of GPT-6.1 series |
| OpenAI | strong | `openai/gpt-6.1-sol` | 2.00 | 10.00 | Below flagship Astra |
| OpenAI | frontier | `openai/gpt-6-astra` | 10.00 | 50.00 | Described as OpenAI's flagship |
| OpenAI | open-weight cheap | `openai/gpt-oss-120b` | 0.01 | 0.037 | |
| Google | cheap | `google/gemini-3.1-flash-lite` | 0.25 | 1.50 | GA, low-latency |
| Google | cheap+ | `google/gemini-3.5-flash-lite` | 0.30 | 2.50 | |
| Google | mid | `google/gemini-3.5-flash` | 1.50 | 9.00 | |
| Google | frontier | `google/gemini-4-argon` | 2.00 | 10.00 | Described as Google's flagship reasoning model |
| Meta Llama | cheap | `meta-llama/llama-4-scout` | 0.10 | 0.30 | No reasoning param. Newest Meta chat model in the list is Llama 4 (Apr 2025) |
| Meta Llama | mid | `meta-llama/llama-4-maverick` | 0.35 | 1.00 | No reasoning param |
| Meta Llama | dense | `meta-llama/llama-3.3-70b-instruct` | 0.59 | 0.79 | |
| Qwen | cheap | `qwen/qwen3.7-flash` | 0.03 | 0.13 | Higher rate above 32k prompt tokens (irrelevant here) |
| Qwen | cheap+ | `qwen/qwen3.8-flash` | 0.15 | 0.47 | |
| Qwen | frontier | `qwen/qwen3.8-max-0902` | 2.00 | 6.00 | 2.4T-param MoE per description |
| Qwen | frontier (fast SKU) | `qwen/qwen3.8-max-prime` | 4.00 | 12.00 | Higher-throughput SKU of Max |
| DeepSeek | cheap | `deepseek/deepseek-v4.1-flash-1017` | 0.15 | 0.60 | **Time-of-day pricing**: the list has overrides at 0.30 / 1.20 during certain UTC windows on weekdays. Window encoding not decoded, so budget at 2x worst case |
| DeepSeek | cheapest | `deepseek/deepseek-v4-flash-0731` | 0.043 | 0.30 | |
| DeepSeek | frontier | `deepseek/deepseek-v4-pro` | 1.60 | 3.20 | Name is "V4 Pro 0423" |
| Mistral | cheap | `mistralai/mistral-small-2603` | 0.15 | 0.60 | "Mistral Small 4" |
| Mistral | mid | `mistralai/mistral-medium-3-5` | 1.50 | 7.50 | |
| Mistral | frontier | `mistralai/mistral-large-4-0` | 0.70 | 2.10 | "Mistral Large 4" |

Notes:
- Anthropic slugs on OpenRouter use dots (`claude-haiku-5.5`). The Anthropic API uses dashes (`claude-haiku-5-5`). Do not mix them.
- The list also holds `:batch` variants at roughly half price (for example `anthropic/claude-haiku-5.5:batch` 0.05 / 0.25) and `:free` variants. How `:batch` models are served and billed (latency, async?) is **unverified**. Do not use them without reading the OpenRouter docs for them.
- The list has about 460 entries and changes quickly. Re-pull the JSON before a full run and diff the prices. Reproduce the table with:
  `curl -s https://openrouter.ai/api/v1/models | jq -r '.data[] | [.id, (.pricing.prompt|tonumber*1e6), (.pricing.completion|tonumber*1e6)] | @tsv'`
- Prices in the list are the headline rate. Per-request routing across providers could change the actual charge. That is why the harness should rely on `usage.cost`, not on this table.

## Budget

### Assumptions (ours, not measured)

- Per harness call: **400 input tokens, 40 output tokens** (system ~75 words + user ~100 words + one-line reply).
- Full run (user's shape): 20 seeds x 10 conditions x agents x 3 rounds, one call per agent per round.
  - low (4 agents): 20 x 10 x 4 x 3 = **2,400 calls**
  - mid (8 agents): 20 x 10 x 8 x 3 = **4,800 calls** (used below)
  - high (12 agents): 20 x 10 x 12 x 3 = **7,200 calls**
- Formula: `call cost = 400 x in/1e6 + 40 x out/1e6`; `run cost = 4,800 x call cost`; `runs = 250 / run cost`.
- Per-call and per-run figures below are computed from the table's per-million prices. No call was made to measure real token counts.

### Results (no hidden reasoning tokens)

| Model | Call arithmetic | $/call | $/full run (4,800) | Range (2,400 to 7,200) | Full runs in $250 |
|---|---|---|---|---|---|
| `anthropic/claude-haiku-5.5` | 400x0.10/1e6 + 40x0.50/1e6 = 0.000040 + 0.000020 | 0.000060 | 0.29 | 0.14 to 0.43 | ~868 |
| `anthropic/claude-sonnet-5.5` | 400x2/1e6 + 40x10/1e6 = 0.000800 + 0.000400 | 0.001200 | 5.76 | 2.88 to 8.64 | ~43 |
| `anthropic/claude-opus-5.5` | 400x4/1e6 + 40x20/1e6 = 0.001600 + 0.000800 | 0.002400 | 11.52 | 5.76 to 17.28 | ~22 |
| `openai/gpt-6.1-terra` | 400x1/1e6 + 40x5/1e6 = 0.000400 + 0.000200 | 0.000600 | 2.88 | 1.44 to 4.32 | ~87 |
| `google/gemini-3.1-flash-lite` | 400x0.25/1e6 + 40x1.5/1e6 = 0.000100 + 0.000060 | 0.000160 | 0.77 | 0.38 to 1.15 | ~326 |
| `deepseek/deepseek-v4.1-flash-1017` | 400x0.15/1e6 + 40x0.60/1e6 = 0.000060 + 0.000024 | 0.000084 | 0.40 | 0.20 to 0.60 | ~620 |
| `qwen/qwen3.7-flash` | 400x0.03/1e6 + 40x0.13/1e6 = 0.000012 + 0.0000052 | 0.000017 | 0.08 | 0.04 to 0.12 | ~3,000 |
| `meta-llama/llama-4-scout` | 400x0.10/1e6 + 40x0.30/1e6 = 0.000040 + 0.000012 | 0.000052 | 0.25 | 0.12 to 0.37 | ~1,000 |

**A full 8-model panel (the eight rows above, one full run each) costs about 0.29 + 5.76 + 11.52 + 2.88 + 0.77 + 0.40 + 0.08 + 0.25 = $21.95**, so $250 buys roughly 11 complete panel sweeps at the mid size.

### Stress case: hidden reasoning tokens

Almost every model above can emit reasoning tokens, billed as output. As an **illustrative assumption** (not measured), add 500 hidden reasoning tokens per call, i.e. 540 output tokens:

| Model | $/call | $/full run | Full runs in $250 |
|---|---|---|---|
| haiku-5.5 | 0.000310 | 1.49 | ~168 |
| sonnet-5.5 | 0.006200 | 29.76 | ~8 |
| opus-5.5 | 0.012400 | 59.52 | ~4 |
| gpt-6.1-terra | 0.003100 | 14.88 | ~17 |
| gemini-3.1-flash-lite | 0.000910 | 4.37 | ~57 |
| deepseek-v4.1-flash-1017 | 0.000384 | 1.84 | ~136 |
| qwen3.7-flash | 0.000082 | 0.39 | ~634 |
| llama-4-scout (no reasoning) | 0.000202 if it did | 0.97 | ~258 |

(The Llama row is shown only to keep the table uniform; Llama 4 Scout has no reasoning parameter, so its real figure is the no-reasoning row above.)

Reading: the input side is almost irrelevant at 400 tokens. **The output side decides the bill**, and the unknown is reasoning tokens. A pilot of ~20 calls per model that records `usage.cost` and `reasoning_tokens` will replace the two assumptions above with measurements; do that before committing to a Sonnet/Opus sweep.

### Guard rails

- Check `GET /api/v1/key` (`limit_remaining`) at start; refuse to start a sweep if projected cost exceeds `OPENROUTER_BUDGET_USD - spent`.
- Track `usage.cost` per call; write it into every log row. Stop at a soft limit of ~90% of the budget.
- Set `max_tokens` high enough for the visible one-line reply plus any reasoning (a reasoning model with `max_tokens=60` may return an empty string). Prefer `reasoning.effort = "none"` (or lowest) where the model allows it, and record which models refuse.
- A key-level spending cap can be set in the OpenRouter dashboard. The `/key` response exposes `limit`, so it exists, but how to set it was **not verified** here.
