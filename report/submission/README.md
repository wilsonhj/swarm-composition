# Paper and editable document

**Who Knows the Goal? Local Context, Task Provenance, and Restricted Assembly When Work Is Split Across Agents**

Author: **Hirokazu James Wilson** · Team HJ · November 7, 2026 edition

- [PDF paper](who-knows-the-goal.pdf) is the frozen export for reading and submission.
- [Word document](who-knows-the-goal.docx) is the editable version of the same edition.
- [Editorial diff](editorial.patch) records the prose revision against [source commit d3322d3](https://github.com/wilsonhj/swarm-composition/commit/d3322d34a5e7fb7e9b4b180d10983b435dc7ab73).
- [Manifest](manifest.json) records file sizes, SHA-256 checksums, source hashes and verification results.

The paper explains the task and scoring in plainer language, removes repeated summaries, and includes the recorded seed-3000 example in the main text. The abstract has 216 words. The main paper occupies pages 1–8; references and appendices bring the full document to 42 pages.

The editorial revision preserves the numerical tables, all 29 references, all four figures and the exact prompts and transcripts in Appendix B. Study 1, Study 2 and development pilots remain separate. The repository's working Markdown draft retains its earlier wording; the editorial diff documents the changes used in these exports without changing frozen research evidence.

## Verification

Both files were checked for the full author name in the visible text and document metadata. The DOCX was rendered to PDF, and all 42 pages were visually reviewed. Structural checks covered 1,522 appendix table-cell strings, 136 exact prompt/transcript lines, source prose coverage, template preservation, embedded fonts, relationship targets and page margins. The main paper meets the eight-page limit, and the PDF is below 25 MB.

All 36 hyperlink targets match the prior export. The retained link audit found 34 reachable targets (HTTP 200/206); two publisher endpoints returned HTTP 403. Those two links could not be confirmed automatically. Links were not re-requested during the editorial revision.

## What belongs in Git

Keep these final PDF and DOCX supplements, their provenance and the editorial diff in Git so readers can retrieve the reviewed edition. Keep temporary exports, page images, build workspaces and local archives under the ignored root `output/` directory. When the paper changes, update both formats and their manifest together so the PDF and editable copy stay aligned.
