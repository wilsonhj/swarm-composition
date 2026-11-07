# Code, claims and evidence audit

Audit date: **7 November 2026, Pacific**. The starting merged main was
`3de7811`; this documentation change builds on PR #5's review fixes at
`8448ea0`. PR #4 remains a separate research-notes proposal. No frozen task,
prompt, collection protocol, raw result or scoring implementation was changed
for this audit.

## What was checked

The audit compared the maintained README, report, video, limitations, related
work, code paths, numerical claim checker, figure generator and replay tools.
Directly relevant publication records and methodological sources are linked in
the [evidence map](methods-evidence.md). The [visual guide](../guide/architecture.md)
was checked against actual calls and information boundaries, with a separate
[worked task](../guide/code-walkthrough.md) executed offline.

This is an audit with an explicit scope, not certification of every sentence in
the repository or independent replication of cited papers. A fetched abstract
checks what the authors report; it does not verify their experiment. Publication
status requires a proceedings, publisher or accepted-track record; absence from
a search index does not prove that a paper was never reviewed.

## Corrections and retained boundaries

| Claim or documentation problem | Correction / evidence |
|---|---|
| Purpose matters **more** than the rule | The video now says local purpose knowledge affected compliance in these experiments. No comparative importance ranking was established across the two different studies. |
| A general statement that restriction-bound agents refuse visible goals | The conclusion is limited to the measured synthetic task and observed solo trials. The report does not establish a universal mechanism. |
| Trusted provenance removed risk | The report states no disclosure was observed in the sampled cells. This is not a guarantee of prevention, trustworthy provenance in deployment, or robustness to forged metadata. |
| "The one leak" was Sonnet | The limitations now acknowledge relay assemblies in both Haiku and Sonnet. Distinct seeds, mixed served-model identity, and repeated same-task runs remain disclosed; event counts are not independent task counts. |
| Separate solo calls imply independent samples | The guide distinguishes context separation from statistical independence. Repeated attempts on one generated task do not create new independent tasks. |
| A small-sample bootstrap interval determines significance | The report distinguishes the descriptive percentile-bootstrap interval from the exact McNemar test. They need not agree at small n. Secondary contrasts are unadjusted. |
| Zero events in fifty trials proves safety | The approximately 5.8% exact one-sided upper bound is conditional on an independent, identically distributed Bernoulli model. It is distinct from the wider two-sided Wilson interval printed per cell and does not quantify external validity. |
| Accepted board and private candidate log are interchangeable | The diagram routes only accepted posts to the assembler/scorer. Workers do not read the board. The monitor sees the trusted objective, accepted history and untrusted proposal; blocked proposals remain private. |
| SAE/persona papers prove this repository's transmission mechanism | SAE steering remains a proposal. Contrastive persona directions, SAE decoder features, text-mediated receiver effects and trained-student transfer are separate concepts. See the evidence map. |
| The bibliography count and Chen/DLab verification flag are current | The research index now points to the current bibliography and PR #5's second-fetch record. It does not repeat stale source counts or call a cited sprint project unlisted. |

Frozen historical documents and analyses remain intact, including disclosed
errata. Their wording is evidence of the original record, not a reason to repeat
an overstated claim in the current report. In particular, rounded `p=0.000` in
archived tables is a display convention; report the exact value or `p < 0.001`,
never a literally zero probability.

## What the automated checks prove

| Check | What it establishes | What it does not establish |
|---|---|---|
| [Numeric claim checker](../../report/tools/check_claims.py) | Specified values recompute from selected raw files; cited-line number pins force review when other numbers change | Coverage of every claim, correctness of prose interpretation, or validity of external research |
| [Historical replays](../handoffs/README.md) | Pinned data/source hashes, reconstruction and reconciliation against recorded evidence | Future hosted-model behavior or scientific replication |
| [Current figure generator](../../report/figures/make_figures.py) | Current scoring agrees with archived cells; regenerated machine-readable plotted values match the committed JSON | Byte-identical images across environments, or proof that every visual encoding is correct |
| [Citation renderer](../../report/tools/render_refs.py) | Report citation keys resolve and the rendered list is current | That the cited paper supports the sentence or has a verified review venue |
| [Guide integrity checker](../guide/tools/check_docs.py) | Maintained local links, function anchors, unique citation keys and reviewed Mermaid/SVG pins match | Semantic correctness of arrows or scientific claims |

The diagram checker deliberately calls its hashes **integrity pins**. Updating
both source and pin requires code review; it does not constitute a semantic
proof. The canonical diagrams were rendered and visually inspected as part of
this change, and the plotted data are checked separately from rendering style.

## Remaining research limits

The repository's experimental design and claims remain the authors' work; they
are not peer-reviewed merely because supporting sources are. The current
evidence is one benign lookup-and-join structure, a small set of fixed prompts,
one provider family, and one trusted-purpose pipeline in the provenance study.
No cross-provider replication, forged-provenance test, local SAE result,
training-mediated transfer or real-world harmful-task validation was added.

Peer-reviewed precedents should support the precise methodological statement
they address. Preprints, workshop proceedings, incident investigations, software
cards and event pages have different roles. Do not convert all of them into
"peer-reviewed evidence". PR #4's marked summary-only event claims require the
primary-source checks described in that PR before use as report facts; they
are not imported into the study results here.

Consensus was used as an additional discovery check. Its complete cited export
was saved separately for the user; search-index venue labels were not treated as
publication-status proof. The repository's source classifications use the
primary records linked in the evidence map.
