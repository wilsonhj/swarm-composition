# Response to external review

Maps each review finding to the action taken and where. "This branch" = the documentation/claims correction branch (README, pilot summaries, related work, report outline, limitations appendix, video script). Engineering items are handled by other agents and are referenced, not claimed here.

## Scientific and interpretive findings

| ID | Finding | Action | Where |
|---|---|---|---|
| A | Headline ("agents that refuse alone become unsafe together") not established by the committed experiments; pilot summaries overbroad | README and report outline reframed around the frozen v2 research question (local-context link; system-level disclosure/assembly vs a single agent with equal opportunity). Current evidence labelled "exploratory framing effects". Pilot summaries corrected: join-policy solo disclosed 0 of 12 target parts (other 7 cells 12/12); strict+explicit was not ~0 everywhere (Haiku pipeline 6/12 parts in `strict_haiku.jsonl`, 4/12 in the explicit sweep); informed coordinators "made no requests in 15 pilot trials (10 Haiku, 5 Sonnet)"; neutral solo baseline already succeeds 3/3; pilot rows lack backend/failed_calls metadata | This branch: `README.md`, `docs/findings/pilot-results.md`, `report/outline.md`, `report/video-script.md` |
| B | Policy and knowledge change together in the v1 relay | Documented as a v1 confound; v2 design (`relay_informed` vs `relay_uninformed` differ only in coordinator task text, same policy for all roles; policy crossed with framing) described in README and Methods | This branch: `README.md`, `docs/findings/pilot-results.md`, `report/outline.md` 3.2/3.3/3.7, Appendix A. Implementation: harness v2, see `experiments/composition-gap/README.md` |
| C | Topology changes opportunity and information (1 vs 5 vs 6 vs up to 36 calls) | Stated explicitly in README, pilot caveats, Methods and Appendix A; report to compare topologies against opportunity-matched solo@k5/solo@k12 with seed-paired contrasts; no causal topology claim | This branch: `README.md`, `docs/findings/pilot-results.md`, `report/outline.md`, `report/appendix-limitations-dual-use.md`. Baselines: harness v2, see `experiments/composition-gap/README.md` |
| D | Proxy interpretation: under `join`, sharing a single part is permitted; strict outcomes test compliance with a synthetic restriction, not trained-in safety | "Proxy interpretation" paragraph in Methods 3.1; new leading limitation in Appendix A; pilot summary notes join-policy part disclosure is not a violation | This branch: `report/outline.md`, `report/appendix-limitations-dual-use.md`, `docs/findings/pilot-results.md` |
| E | Scoring imperfections | Four outcome measures defined in Methods and Appendix A (scoring definitions, heuristics, normalisation, wrong-position handling flagged as DECIDE); legacy metrics retained for comparison | Doc side: this branch (`report/outline.md` 3.4, appendix). Scoring: `scoring.py` / `analyze.py`, see `docs/findings/pilot-rescored.md` |
| F | Pilots selected the design | "Pilot -> design changes" paragraph (Methods 3.7); held-out seeds 1000-1019; v1 full run treated as exploratory replication; "design selected on pilot seeds" limitation | This branch: `report/outline.md`, `report/appendix-limitations-dual-use.md`, `README.md` |

## Engineering findings

| Finding | Action | Where |
|---|---|---|
| Anthropic failures counted as PASS | Per-row `failed_calls`; analysis excludes failed rows and reports them separately (described in Methods 3.5) | harness v2 — see `experiments/composition-gap/README.md` |
| Spend cap not hard | Hard cap enforcement | harness v2 — see `experiments/composition-gap/README.md` |
| Relay request metric bug | Harness records turns; `requested` = coordinator's first turn posted (regression test). Pilot counts re-scored: Haiku relay_uninformed 4/10 → 1/10 | harness v2 — see `experiments/composition-gap/README.md`; `scoring.py`, `docs/findings/pilot-rescored.md`, `docs/findings/pilot-results.md` |
| Invalid condition names | Validation of condition names | harness v2 — see `experiments/composition-gap/README.md` |
| Rerun duplication | Dedup / no-overwrite handling of reruns | harness v2 — see `experiments/composition-gap/README.md` |
| Summaries include failed rows | Analysis excludes failed rows, reports counts | scoring.py / analyze.py — see `docs/findings/pilot-rescored.md`; denominators in this branch (`report/outline.md` 3.5) |
| Incomplete provenance | Run manifests (run id, commit, prompt hash, CLI version), per-turn logs | harness v2 — see `experiments/composition-gap/README.md`; reproducibility note in `report/outline.md` 3.6/B.8 |
| Claude Code env inheritance | Environment isolation for the `claude -p` backend | harness v2 — see `experiments/composition-gap/README.md` |
| Unpinned dependencies | Pinning; residual unpinned provider defaults/CLI versions disclosed as a limitation | harness v2 — see `experiments/composition-gap/README.md`; limitation in this branch (appendix) |
| Narrow secret scanning | Broader scanning | CI / tooling — see `experiments/composition-gap/README.md` (not changed on this branch) |
| Literature novelty claims | `related-work.md` no longer claims prior work conflates agent- and system-level safety or always requires an adversarial participant. Srivastav & Zhang (REALM 2025) fetched and described as close prior work; Semantic Intent Fragmentation (Ahad et al., 2026) added; Apart DLab project page fetched once and described as early, unreviewed sprint work (still flagged) | This branch: `docs/research/related-work.md`, `docs/research/README.md`. New BibTeX keys `ahad2026semantic`, `chen2026theysay` still need adding to `references.bib` |
| Overbroad pilot summaries | See finding A | This branch: `docs/findings/pilot-results.md` |
| "Self-organising" overstates the protocol | Replaced with "fixed round-robin shared board" in all files owned by this branch | This branch: `README.md`, `docs/research/related-work.md`, `report/outline.md` |

## Architectural audit (Nov 6, 2026)

Every factual claim was checked against the code at c9a4617.
- **Accurate:** 17 of 20 claims.
- **Inaccurate:** claim 3 said pilot manifests are committed; none exist, and the full and v2 results were untracked at audit time. Claim 15 said raw row fields embed failed-call PASS data; in v2, a failed call posts nothing.
- **Minor:** the test count was 117 passed plus 1 skipped, not 118 passing.

| Audit item | Verdict | Action |
|---|---|---|
| Module globals `SYS`/`FRAME` | No validity risk. They are set once before any thread starts, and 37 shuffled test orders all passed. | None |
| Duplicated parsing (`parse_post` vs `post_text`) | No effect on v2 numbers, because v2 turns carry the harness's parse. Every reply so far is `POST:` or `PASS`. | Documented. Run the off-format check before the final analysis. |
| Single-experiment scope | By design. | None |
| `claude -p` has no max-tokens cap | Not binding for Haiku: the longest reply was 32 characters. A real risk for OpenRouter reasoning models: an empty or truncated reply would score as PASS. | Before any OpenRouter run, treat `finish_reason == "length"` or empty content as a failed call (harness change deferred until the v2 run finishes). |
| Retry-then-PASS | Failed rows are already excluded from every rate and paired contrast. | `analyze.py` now prints the failed-row count and warns on duplicate (cell, seed) rows. |
| *Found while checking the audit:* `solo@kK` metrics pooled across attempts | **Bug.** It inflated the opportunity-matched baseline. | Fixed: `scoring.py` now scores each attempt on its own and takes the best. Regression test added. |
| *Found while checking the audit:* relay ignores framing | Design property. | Documented in the report methods (3.5). `analyze.py` has a relay-request table. |
