# CLAUDE.md

Hackathon research repo (Swarm Alignment Hackathon, Nov 6–8 2026, Track 2). See README.md for the question and layout.

## Ground rules
- Made-up results or references can disqualify the team (Apart rules). Only cite sources you have fetched; add them to `docs/research/references.bib`. Report only numbers from frozen runs.
- Only weekend work counts. Label any pre-existing code.
- Never read, print or commit `.env`. Keys load at runtime from env or the repo-root `.env`.
- OpenRouter spend comes from a fixed $250 credit: run `make credits` before big runs and always pass `--max-usd`.

## Running
- Python 3.11, stdlib-only harness: `cd experiments/composition-gap && uv run --no-project python harness.py ...`
- Tests: `make test` (no network). Smoke: `make smoke`.
- The `claude-code` backend shells out to `claude -p` on the user's subscription (ANTHROPIC_API_KEY stripped; `--bare` not usable because it forces API-key auth).

## Results
- Write new runs under `experiments/composition-gap/results/`; the harness refuses to overwrite (`--append` to add) and writes a `.manifest.json` per run.
- Runs from buggy code go to `results/**/superseded/` with a note in `docs/findings/`.
- Pilot numbers are preliminary; the report uses only the frozen full run.

## Design versions
- **v2 (default, frozen):** one policy (`none`/`strict`) for every role, crossed with framing; opportunity-matched `solo@kK` baselines; relay_informed vs relay_uninformed differ only in coordinator task text; held-out seeds 1000+. Confirmatory run: `run_v2.sh`. Score and analyse with `scoring.py` / `analyze.py` (valid rows only, CIs, seed-paired contrasts).
- **v1 (`--design v1`, `run_full.sh`):** exploratory only. Its relay changed policy and knowledge together, and stored relay `requested` values are inflated; always rescore v1 rows with `scoring.py`.
- External review and our responses: `docs/findings/review-response.md`.
