# Paper and editable document

**Who Knows the Goal? Local Context, Task Provenance, and Restricted Assembly When Work Is Split Across Agents**

Author: **Hirokazu James Wilson** · Independent researcher · November 8, 2026

- [Read the PDF](who-knows-the-goal.pdf) — 15 pages total.
- [Edit the Word document](who-knows-the-goal.docx) — the same content and layout.

The main text occupies pages 1–5, references page 6, and appendices pages 7–15. The five-page main text meets the official eight-page cap; the nine appendix pages also meet the author's ten-page budget. Body font size and margins are unchanged.

The final scientific revision sharpens the contribution, separates supplied purpose from authenticated provenance, and explains the limits of the controls and monitor comparison. Table 2 now uses complete-pair denominators for both conditions; its caption retains the all-valid marginal count. All six figures remain. Fifteen directly relevant references replace the broader twenty-nine-entry list, which remains in the repository. The abstract is 193 words. The [current manuscript](manuscript.md), [appendices](appendices.md) and [selected references](references.md) supply this edition's content.

The final correction pass also discloses the exploratory Sonnet extension separately, identifies the stopped v1 run accurately, distinguishes stored replies from reconstructed inputs, and attributes sprint timing to the author with the timestamp limitation. The two bibliography names now render as Chen, Y.-H. and Wagner III, L. T. The [final verification record](final-corrections-verification.json) records these checks and fresh replays.

## Evidence and verification

This edition replaces the earlier sixteen-page revision of the original twenty-page export. Exhaustive records remain available as repository supplements:

- [Full methods, tables and transcripts](supplements/extended-methods-and-results.md), including all exact prompt templates.
- [Extended limitations and ethics](supplements/extended-limitations.md).
- [Critical scientific review and comparison with recent academic papers](research-review.md).
- [Independent outcome checks](data-quality/review-check.py), [results](data-quality/review-results.json) and [review verification](research-review-verification.json).
- [Earlier fact-check and study-completion assessment](fact-check.md), retained as a historical record.
- [Data-quality checks](data-quality/check.py) and [results](data-quality/results.json).
- [Secondary calculations](secondary-metrics.py) and [output](secondary-metrics.txt).
- [Editable diagram sources](figures/) and their generation script.

The paper links to commit-pinned supplements. The [editorial patch](editorial.patch) records the earlier editorial revision from [source commit d3322d3](https://github.com/wilsonhj/swarm-composition/commit/d3322d34a5e7fb7e9b4b180d10983b435dc7ab73); it does not reconstruct the current shorter edition. Use the current manuscript and appendices linked above for this edition. The repository's working `report/draft.md` retains its earlier wording. Frozen runs and protocols are unchanged, and no new model experiments were run.

All fifteen final pages were visually reviewed, directly or through pixel identity with the preceding reviewed render. Checks cover source text and tables, six unchanged figures, fifteen selected references, author metadata, embedded fonts, template preservation and margins. Independent scoring agrees with repository outcomes on all 1,840 confirmatory study records and, separately, the 160 disclosed exploratory-extension records. Both canonical offline replays pass on fresh pinned worktrees, and forty GitHub blob identities match the local result files. The main tables, all sixteen Study 2 cells and appendix paired comparisons reproduce. The [length verification](length-verification.json), [research review verification](research-review-verification.json) and [manifest](manifest.json) record checksums and scope. Offline replay does not establish fresh behavioral replication.

The [November 8 Guidelines check](guidelines-check.md) applies to this edition. The required limitations and dual-use appendix is on page 7. The author has confirmed participation in at most two global projects. Global upload and receipt of a submission confirmation remain separate from document readiness.

## What belongs in Git

Keep final PDF and Word editions, supporting evidence and source provenance here so readers can retrieve the reviewed documents. Keep temporary exports, page images, build workspaces and local archives under the ignored root `output/` directory. Update both formats and their manifest together.
