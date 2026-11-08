# Paper and editable document

**Who Knows the Goal? Local Context, Task Provenance, and Restricted Assembly When Work Is Split Across Agents**

Author: **Hirokazu James Wilson** · November 7, 2026

- [Read the PDF](who-knows-the-goal.pdf) — 20 pages total, including references and appendices.
- [Edit the Word document](who-knows-the-goal.docx) — the same content and layout.

The eight-page main paper distinguishes Study 1's comparison of framing and coordination from Study 2's test of trusted task purpose. Six figures include a study overview, a worked trial from inputs to scored outputs, coordination diagrams, a result heatmap, and a safety/utility comparison. The abstract is 196 words.

## Evidence and verification

The compact edition replaces the 43-page export. It retains the primary findings, full-study counts, uncertainty, failure accounting and scientific limits. Exhaustive records remain available as repository supplements:

- [Full methods, tables and transcripts](supplements/extended-methods-and-results.md), including all exact prompt templates.
- [Extended limitations and ethics](supplements/extended-limitations.md).
- [Fact-check and study-completion assessment](fact-check.md).
- [Data-quality checks](data-quality/check.py) and [results](data-quality/results.json).
- [Secondary calculations](secondary-metrics.py) and [output](secondary-metrics.txt).
- [Editable diagram sources](figures/) and their generation script.

The paper links to commit-pinned supplements. The [editorial patch](editorial.patch) reconstructs the revised manuscript from [source commit d3322d3](https://github.com/wilsonhj/swarm-composition/commit/d3322d34a5e7fb7e9b4b180d10983b435dc7ab73); the repository's working Markdown retains its earlier wording. Frozen runs and protocols are unchanged, and no new model experiments were run.

All 20 rendered pages were visually reviewed. Checks cover source text and table values, six figures, 29 references, author metadata, embedded fonts, template preservation and margins. The [manifest](manifest.json) records checksums and the precise verification scope. Historical external-reference link checks remain documented there; the bibliography was not re-audited in this layout pass.

## What belongs in Git

Keep final PDF and Word editions, supporting evidence and source provenance here so readers can retrieve the reviewed documents. Keep temporary exports, page images, build workspaces and local archives under the ignored root `output/` directory. Update both formats and their manifest together.
