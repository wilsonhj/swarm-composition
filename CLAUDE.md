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
- **task-provenance-v1 (prospective):** separate `provenance.py` runner and `docs/protocols/task-provenance-v1.md`; fixed pipeline, paired authorized/restricted tasks, local/provenance/monitor conditions. Default mock only. Preserve v1/v2 prompts and all existing results. Pilot seeds 2000–2999; held-out 3000–3049 only after a clean committed protocol freeze. Do not infer preregistration from seed numbers.
- **v2 (default, frozen):** one policy (`none`/`strict`) for every role, crossed with framing; opportunity-matched `solo@kK` baselines; relay_informed vs relay_uninformed differ only in coordinator task text; held-out seeds 1000+. Confirmatory run: `run_v2.sh`. Score and analyse with `scoring.py` / `analyze.py` (valid rows only, CIs, seed-paired contrasts).
- **v1 (`--design v1`, `run_full.sh`):** exploratory only. Its relay changed policy and knowledge together, and stored relay `requested` values are inflated; always rescore v1 rows with `scoring.py`.
- External review and our responses: `docs/findings/review-response.md`.

## Analysis integrity
- Never silently merge study/design/backend/model/authorization/run/prompt/protocol metadata. Duplicate trial keys are errors; select a run explicitly instead of taking the first row.
- Repeated solo primary scores use the best single attempt; `pooled_*` diagnostics have a different observer threat model.
- Report authorized utility alongside restricted disclosure. Monitor-blocked proposals are private logs, not accepted board posts.
- `--max-usd` is an estimated threshold, not a guaranteed hard cap. Actual costs and retries can exceed reservations.

## Submission memo and study boundaries
- See `docs/research/revised-sae-review-and-submission-memo.md` and the source-linked `docs/findings/development-timeline.md`. Do not label all work preceding an amendment as pre-sprint; verify assets individually.
- Preserve completed v2 results, the provenance development pilot, and the unimplemented SAE proposal as distinct studies. Do not replace the provenance primary comparison with the supplied memo's unmatched N8/K12 comparison.
- Three-round swarm@nN has at most 3N calls; N8 matches a K24 maximum, N4 a K12 maximum, and six-call relay needs K6. Report realized calls and stopping rules too.
- Offline `power.py` enumerates hypothetical paired designs. It does not establish observed effects, actual study power, or independence of repeated task seeds.
