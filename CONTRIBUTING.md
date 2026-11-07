# Contributing

Swarm Alignment Hackathon (Apart Research), Nov 6-8 2026. Team of up to 5. Keep changes small and results reproducible.

## Quickstart

```bash
cp .env.example .env      # then edit .env: set OPENROUTER_API_KEY and OPENROUTER_BUDGET_USD
make credits              # confirm the key works and see remaining budget
make test                 # pytest, no network
make smoke                # mock-backend end-to-end run
make help                 # list all targets
```

Requires [uv](https://docs.astral.sh/uv/). The harness uses only the stdlib for the mock, claude-code and openrouter backends. `.env` is gitignored; never commit it or paste keys anywhere (CI fails if it finds one).

## Branches

`<type>/<short-topic>`, where type is one of `exp`, `feat`, `fix`, `docs`, `report`, `ci`. Examples: `exp/haiku-strict-neutral`, `fix/openrouter-retry`, `docs/related-work`. Branch off `main`, open a PR, and get one teammate to look before merging.

## Commits

Short imperative subject, prefixed with the same type: `exp: add haiku strict/neutral pilot`, `fix: handle empty completion`. One logical change per commit. Do not commit API keys, `.env`, or large scratch outputs.

## Results conventions

- Location: `experiments/composition-gap/results/`.
- Filename: `results/<date>_<model>_<policy>_<framing>.jsonl`, e.g. `results/2026-11-06_claude-haiku-5-5_strict_neutral.jsonl` (replace `/` in model ids with `-`).
- Never overwrite or edit an existing results file. Re-runs get a new file.
- If a run is superseded (bug fix, bad config), move it to a `superseded/` folder next to it (e.g. `results/superseded/`) and add a short note (a `.md` beside it or a line in the PR) saying why and which run replaces it.
- `results/pilot/` holds early runs; keep it as is.
- Record the exact command used (and harness commit) in the PR or the experiment-run issue.

## Budget etiquette

- Run `make credits` before any large run, and tell the team in chat when you start one.
- Always pass `--max-usd` for the openrouter backend (`make run-openrouter` defaults to `MAX_USD=25`, `SEEDS=20`). Pilot with the mock backend or few seeds first.
- Estimate cost in an experiment-run issue before runs that could cost more than a few dollars.

## Integrity rules

- Weekend-only: only work done during the hackathon (Nov 6-8 2026) counts.
- Label pre-existing code: anything written before the hackathon must be clearly marked as such in the file/README and ticked in the PR checklist.
- Verify every citation: open the source and confirm it says what we claim. Fabricated citations can disqualify the project. If you cannot verify it, leave it out.
- Never commit API keys.

## Adding a new experiment

1. Create `experiments/<name>/` (follow `experiments/composition-gap/` as a model).
2. Include a short `README.md` (question, how to run, expected outputs), the entry script, a `tests/` directory runnable offline, and a `results/` directory.
3. Keep a mock/offline backend so CI can smoke-test it without secrets.
4. Add `make` targets for it (or ask for them in the PR) and extend `.github/workflows/ci.yml` with its test and smoke commands.
5. Write up findings in `docs/findings/` and link the result files.
