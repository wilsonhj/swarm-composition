# Developer reference (docs/dev)

All facts fetched 2026-11-06 from the sources linked in each file; unconfirmed items are labelled "unverified".

- [openrouter.md](openrouter.md): OpenRouter backend: auth, base URL, chat-completions shape, `usage.cost`, credit check (`/key`, `/credits`), 402/429 handling, model slug and price table across seven families, and a dollar budget for a full run on the $250 credit.
- [claude-code-cli.md](claude-code-cli.md): how the harness drives `claude -p` headless, what each flag does, why `ANTHROPIC_API_KEY` is stripped, what `total_cost_usd` means, and subscription limits.
- [anthropic-api.md](anthropic-api.md): Messages API basics and the current Claude model IDs and prices (short).
- [datasets.md](datasets.md): Swarm Traces, AI Village (gated), Moltbook and the Transluce urlquery data: contents, format, access, licence, and how each could support a composition-gap study.
