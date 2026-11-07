# Claude Code CLI backend (`claude-code`)

Facts fetched **2026-11-06** from the pages linked below. Items not confirmed there are marked **unverified**.

Sources:
- CLI reference (flags): https://code.claude.com/docs/en/cli-reference
- Run Claude Code programmatically (`-p`, output formats, bare mode): https://code.claude.com/docs/en/headless
- Authentication and precedence: https://code.claude.com/docs/en/authentication
- Cost tracking (what `total_cost_usd` is): https://code.claude.com/docs/en/agent-sdk/cost-tracking
- Manage costs / usage limits: https://code.claude.com/docs/en/costs

## What the harness runs

```
claude -p <user> --safe-mode --model M --system-prompt S --tools "" \
       --strict-mcp-config --no-session-persistence --output-format json
```

- `ANTHROPIC_API_KEY` removed from the child environment.
- Working directory: a fresh temp dir per call.
- Reads `total_cost_usd` (and the reply from `result`) out of the JSON on stdout.

## Flags, one by one

| Flag | What the CLI reference says | Why the harness uses it |
|---|---|---|
| `-p` / `--print` | Print response without interactive mode | Headless, one prompt in, one answer out |
| `--safe-mode` | Starts with all customizations disabled: CLAUDE.md, skills, plugins, hooks, MCP servers, custom commands and agents, output styles, workflows, themes, keybindings, status line, LSP servers and auto memory do not load. Authentication, model selection, built-in tools and permissions work normally ("which differs from `--bare`"). Managed settings policy still applies, including policy-configured hooks. | Keeps the user's personal `~/.claude` setup (including the global CLAUDE.md) out of agent prompts, **without** forcing API-key auth like `--bare` does |
| `--model M` | Alias (`sonnet`, `opus`, `haiku`, `fable`) or a full model name, for example `claude-sonnet-5`. Overrides the `model` setting and `ANTHROPIC_MODEL`. | Select the model per call. Prefer full IDs (for example `claude-haiku-5-5`) in logs so a moving alias cannot change results silently |
| `--system-prompt S` | Replaces the entire system prompt with custom text. The headless page adds: when you replace it, the run also starts without the git-status snapshot. | The agent's persona/policy prompt is the only system text |
| `--tools ""` | Restricts built-in tools. `""` disables all. The flag does not affect MCP tools. A list that omits `EndConversation` does not remove it; `""` removes it only when no MCP tools remain. | Agents must answer in text, not act |
| `--strict-mcp-config` | Only use MCP servers from `--mcp-config`, ignoring all other MCP configurations | With no `--mcp-config` given, this means no MCP servers at all |
| `--no-session-persistence` | Sessions are not saved to disk and cannot be resumed. Print mode only. | No transcript litter, and no accidental cross-call state |
| `--output-format json` | Options: `text`, `json`, `stream-json`. `json` gives structured JSON with the result, session ID and metadata; the text answer is in `result`. | Machine-readable reply plus cost |

Not used, but relevant:
- `--bare`: skips hooks, skills, plugins, MCP servers, auto memory and CLAUDE.md for faster, reproducible scripted calls, **but** "bare mode doesn't use your subscription login": it never reads OAuth credentials or the keychain and needs `ANTHROPIC_API_KEY` or `apiKeyHelper`. That is why it was rejected. The headless page says `--bare` is recommended for scripted calls and "will become the default for `-p` in a future release". Re-check this when upgrading Claude Code, because it could change what `--safe-mode` runs look like.
- `--max-budget-usd` (print mode only): stops the run once *estimated* spend reaches the amount. Not passed today. Spend can overshoot the cap. Single-call runs gain little from it.
- `--max-turns`: limit agentic turns (print mode only). With no tools there should be one turn. **Unverified** whether passing `--max-turns 1` is harmless in this setup, so it is not recommended without a test.

## What `--output-format json` returns

Verified from the headless and cost-tracking pages:
- `result`: the text answer.
- `session_id`.
- `total_cost_usd`: cumulative estimated cost of the call.
- `usage` and `modelUsage` (per-model token counts and `costUSD`). Output tokens in `usage`/`modelUsage` come from the result message; read them there rather than from per-step data.
- Error runs also carry `total_cost_usd` and `usage`; the result `subtype` distinguishes success from error kinds.

Exit status: 0 on success, non-zero on failure. "When a failure happens inside the run, such as missing authentication, Claude Code prints the failure as the result on stdout", so exit code alone is not enough. Parse the JSON and check the error indicator. The exact error-flag field name (for example `is_error`) was **not shown** on the fetched pages. Print one failing example (bad model name) and pin the field before relying on it.

Sizes: piped stdin is capped at 10 MB (not relevant for 40-150 word prompts). The user prompt is passed as an argv string; OS argv limits are not a concern at this size, but avoid control characters/NULs.

## Why `ANTHROPIC_API_KEY` is stripped

Authentication precedence (authentication page), highest first: cloud-provider variables; `ANTHROPIC_AUTH_TOKEN`; **`ANTHROPIC_API_KEY`**; `apiKeyHelper`; `CLAUDE_CODE_OAUTH_TOKEN`; Anthropic profiles; **subscription OAuth from `/login`** (last). And: "In non-interactive mode (`-p`), the key is always used when present." The page also warns that a set key beats an active subscription and can fail if the key's organisation is disabled.

So if the developer's shell has `ANTHROPIC_API_KEY` exported (for the `claude` API backend), `claude -p` would silently bill that key instead of using the subscription. Removing the variable from the child env forces the subscription path. `CLAUDE_CODE_OAUTH_TOKEN` and `ANTHROPIC_AUTH_TOKEN` are also higher-precedence than `/login`. Strip or deliberately set them too if the harness might run on a machine that has them (the code only strips the API key). If `/status` shows an unexpected credential, check these.

## Cost reporting: what the number means

- `total_cost_usd` is a **client-side estimate** computed from a price table bundled with the CLI (list prices, unless a managed `modelPricing` table applies). It "can drift from what you are actually billed" and is not billing data (cost-tracking page).
- For a Pro/Max/Ultra subscriber, usage is "included in their subscription", so the dollar figure is not what is charged (costs page). It is still the right yardstick for comparing against OpenRouter spend and for the paper's cost columns: say "estimated list-price cost".
- Models whose ID the installed CLI does not recognise may be priced wrongly (cost-tracking page). Record `claude --version` with every run.
- Cost for a subscription call has a different budget: plan usage windows (below), not dollars.

## Limits

- Subscription plans meter usage in windows. The costs page describes a rolling five-hour window plus a weekly window for Team/Enterprise seats, and for individuals, "plan usage" bars and "usage credits" past the limit. Hitting it produces "You've hit your session limit" or "weekly limit" errors, shared across models (switching model does not help, except after a model-family-specific message). Exact allowances for the user's plan are **unverified**.
- A full run of ~4,800 calls (see `openrouter.md` for the sizing) on a subscription will very likely hit a window. Run the Claude Code backend for pilots and small cells, and use OpenRouter for the full sweep, or checkpoint and resume across windows.
- API-level rate limits on subscription traffic and safe concurrency are **unverified**. Start with 2-4 concurrent processes and watch for `rate_limit` errors. The headless page documents `system/api_retry` events with error categories such as `rate_limit`, `overloaded`, `authentication_failed`, `billing_error`, but that stream is only emitted with `stream-json`, not `json`.
- Thinking: the costs page says you cannot turn off thinking on Opus 5.5, Sonnet 5.5, Haiku 5.5 or the Fable models, which "always use extended thinking". Thinking tokens are billed as output tokens and will appear in `total_cost_usd` even for one-line replies. Effort can be lowered with `/effort` or `/model`. Whether a non-interactive flag/env for effort exists in the installed version is **unverified**. Check `claude --help`.
- Startup overhead per process (hundreds of ms or more) is **unverified**; measure it before estimating wall time.
- Behaviour differs from the raw API: Claude Code adds its own request machinery. With `--system-prompt` replaced and no tools, the prompt should be close to the plain system/user pair, but exact token counts will not match an API call. If you compare Claude Code to OpenRouter-served Claude models, compare `usage` token counts too, not just the replies.

## Reproducibility checklist

Log per call: CLI version, model ID as passed, flags, `total_cost_usd`, `usage`, `modelUsage`, `session_id`, and the run date. Because `--safe-mode` still applies managed-settings policy, a managed policy on the machine could change behaviour: note it if you run on a corporate laptop.
