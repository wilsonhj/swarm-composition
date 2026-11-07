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
- Write new runs to `experiments/composition-gap/results/<date>_<model>_<policy>_<framing>.jsonl`; never overwrite.
- Runs from buggy code go to `results/**/superseded/` with a note in `docs/findings/`.
- Pilot numbers are preliminary; the report uses only the frozen full run.

## Known design issue
The strict policy text names the "vault passphrase" in every agent's system prompt, so "uninformed"/"neutral" agents are not truly uninformed. Fix before the full run: only the informed party sees the passphrase-naming policy.
