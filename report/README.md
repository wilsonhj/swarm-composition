# report/

Submission drafts for the Swarm Alignment Hackathon (Apart Research + AI Alignment Foundation), Track 2: The Science of Agent Networks.

## Files
- `draft.md`: working report covering two separate studies: the completed v2 Haiku/Sonnet measurements and the task-provenance study (development pilot plus the completed held-out Haiku run, never pooled with v2). Remaining TODO is final layout. SAE work is an unimplemented proposal only.
- `figures/`: figure scripts and rendered images for the report.
- `references.md`: rendered references (generated from `../docs/research/references.bib` by `tools/render_refs.py`).
- `tools/render_refs.py`: script that renders `references.md`.
- `appendix-b.md`: Appendix B draft.
- `claim-ledger.csv`: ledger tying each report claim to its source.
- `outline.md`: full 8-page report skeleton with target lengths and `[RESULT]` / `[PILOT]` placeholders (pilot numbers must not appear in the final text).
- `appendix-limitations-dual-use.md`: draft of the REQUIRED appendix "Limitations and Dual-Use / Ethical Considerations".
- `video-script.md`: timed 3-minute script, visuals, and recording checklist (LA hub).
- Related work lives in `../docs/research/related-work.md` (written separately; cite only what it verifies).
- [Corrected submission memo](../docs/research/revised-sae-review-and-submission-memo.md): checked call budgets, literature corrections, hypothetical power and release scope. [Development timeline](../docs/findings/development-timeline.md): per-item UTC/Pacific provenance; earlier repository work is not automatically pre-sprint.

## Deadlines
| Deliverable | Deadline | Source |
|---|---|---|
| Global report (PDF, max 8 pages excluding references and appendices, abstract 150-250 words, PDF <= 25 MB) | Sun Nov 8 2026, 23:59 AoE | https://apartresearch.com/sprints/swarm-alignment-2026 |
| LA hub 3-minute video | Sun Nov 8 2026, 10:00 AM PT | https://aialignmentfoundation.org/hackathons/swarm-alignment-2026 |
| LA hub live presentations (top 15 only; 10 min) | Sun Nov 8, 12:00-3:00 PM PT (finalists announced 11:00 AM-12:00 PM PT) | same |

Video format and submission location are not specified on either page; see TODOs in `video-script.md`.

## Building the PDF
Apart's official template is a Google Doc (not LaTeX/Overleaf):

1. Open the copy link: https://docs.google.com/document/d/1_1_27EyZriMlc8n8EBE2YScaeyMjm-8xjR097nmHXAE/copy?usp=sharing
   (The sprint page says to use the template linked on its Guidelines tab, https://apartresearch.com/sprints/swarm-alignment-2026#guidelines, since the one in an acceptance email may be older. Re-check that the link still matches.)
2. Make a copy in your own Drive, then paste the completed sections from `draft.md` and Appendix A from `appendix-limitations-dual-use.md`; use `outline.md` as a planning checklist. Resolve author/figure/layout TODOs and cite the correct study/version before export.
3. File > Download > PDF (.pdf). Check: body <= 8 pages (references and appendices excluded), abstract 150-250 words, authors/affiliations present, Appendix titled "Limitations and Dual-Use / Ethical Considerations", file <= 25 MB.
4. Submit via the form on the Apart sprint page. To replace a submission, resubmit with the same title before the deadline (do not email the PDF). Required fields: project title, abstract, PDF, interest in publishing, at least one track, team name, location, team member 1 name and email.

## Judging (per coordinator, from the event pages; details in ../docs/hackathon/)
- Global: three dimensions scored 1-5: Impact Potential & Innovation; Execution Quality; Presentation & Clarity.
- LA hub: Idea (novelty and relevance); Soundness & execution; Results; Clarity & presentation.
- Disqualification wording: "made-up results or references". Report only numbers from the frozen full run; cite only fetched sources (`../docs/research/references.bib`).
- Submission form requires team name and location; PDF <= 25 MB.
- Pre-existing code must be marked in BOTH the repo README and the report. The author confirmed there is none; both now say so.
- LA video upload method and format are NOT stated on either page: TODO ask the LA organisers (also in `video-script.md`).

## Rules to remember
- Only weekend work is judged. Disclose genuinely pre-sprint work/code in README and report after item-specific verification. The recorded v2 execution is during the event; do not label it pre-event just because it precedes an amendment. See the [timeline](../docs/findings/development-timeline.md).
- Optional extras: public GitHub repo, 3-5 minute demo video, slides (<= 25 MB).

Official requirements were rechecked on 7 November 2026: the eight-page limit excludes references **and appendices**; abstract 150–250 words; official template and limitations/dual-use appendix required. The global deadline is Nov 8 at 23:59 AoE; LA's three-minute video deadline is Nov 8 at 10:00 Pacific. Sources are the [Apart guidelines](https://apartresearch.com/sprints/swarm-alignment-2026#guidelines) and [LA schedule](https://aialignmentfoundation.org/hackathons/swarm-alignment-2026). The Markdown memo is not the final template PDF.
