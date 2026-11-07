# Swarm Composition — "Safe alone, dangerous together?"

Swarm Alignment Hackathon, Nov 6–8 2026 (Apart Research × AI Alignment Foundation) · LA hub @ AE Studio + global sprint · **Track 2: Science of agent networks**

**Question:** do LLM agents that refuse to produce a forbidden artifact on their own still produce it when the work is split across several agents — a pipeline, a self-organising swarm on a shared board, or a coordinator relaying sub-requests?

Benign proxy: the forbidden artifact is a 4-word "vault passphrase"; each word is a trivial lookup held by a different agent. String-match scoring, no LLM judge.

## Deadlines

| Deliverable | Due |
|---|---|
| LA hub 3-minute video | Sun Nov 8, 10:00 PT |
| Global report (≤8-page PDF, Apart template, Limitations & Dual-Use appendix) | Sun Nov 8, 23:59 AoE |

Details and verification: [docs/hackathon/](docs/hackathon/).

## Quickstart

```bash
cp .env.example .env        # then paste your OpenRouter key into .env
make credits                # check remaining OpenRouter credit
make test                   # unit tests, no network
make smoke                  # mock-backend run
```

Run an experiment (see [experiments/composition-gap/README.md](experiments/composition-gap/README.md)):

```bash
cd experiments/composition-gap
uv run --no-project python harness.py --backend claude-code --model claude-haiku-5-5 \
  --policy strict --framing neutral --seeds 20 --out results/2026-11-07_haiku_strict_neutral.jsonl
uv run --no-project python harness.py --backend openrouter --model <provider/model-slug> --max-usd 25 ...
```

Backends: `claude-code` (local Claude Code subscription), `openrouter` ($250 LA compute credit; key in `.env`), `claude` (Anthropic API), `mock`.

## Layout

```
experiments/composition-gap/   harness, tests, results/ (pilot runs in results/pilot/)
docs/hackathon/                event overview, deadlines, rules, submission checklist
docs/research/                 verified bibliography, METR incident summary, related work, references.bib
docs/dev/                      OpenRouter, Claude Code CLI, Anthropic API, datasets, budget
docs/findings/                 pilot results and running notes
report/                        8-page report outline, Limitations & Dual-Use appendix, video script
```

## Status

- Pilots done (Fri): [docs/findings/pilot-results.md](docs/findings/pilot-results.md).
- Next: fix the system-prompt policy confound, freeze the design, run 20 seeds/cell on Haiku + Sonnet, then cross-model via OpenRouter.

## Integrity

All code here was written during the hackathon weekend (started Fri Nov 6, 2026). Every citation in `docs/research/` was fetched and verified; unverified items are listed separately. Never commit `.env`.
