"""Report data figures, computed from the frozen raw results with the repo's own scoring/analysis code.

    uv run --no-project --with matplotlib python report/figures/make_figures.py

Inputs (read only):
  * Study 1 (v2): experiments/composition-gap/results/v2/*.jsonl (never superseded/).
  * Study 2 (task provenance, held out): experiments/composition-gap/results/task-provenance/heldout-haiku.jsonl.
The two studies are loaded, summarised and plotted separately; they are never pooled.

Every plotted cell is computed with analyze.summarize (scoring.score_row underneath) and then cross-checked
against the committed analysis markdown for the same files; any missing or mismatched cell aborts the script
before a figure is written. No model calls. Fixed SVG hash salt and absent timestamps reduce rendering
variation within one environment; image bytes can differ across library, font and platform versions.

Outputs (report/figures/ by default; use --out-dir to change):
fig2_v2_heatmap.{png,svg}, fig4_provenance_heldout.{png,svg}, figure-data.json.
fig3_v2_swarm_size is skipped when the frozen v2 data hold only one swarm size (they do: swarm@n4 only).
"""
import argparse
import json
import sys
import textwrap
from pathlib import Path

sys.dont_write_bytecode = True  # never write __pycache__ under experiments/

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments" / "composition-gap"
RES = EXP / "results"
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(EXP))

import analyze  # noqa: E402  (repo code: load_rows, enrich, summarize, wilson)
from scoring import is_preschema  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "svg.hashsalt": "swarm-composition-figures", "svg.fonttype": "path",
    "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e", "ytick.color": "#52514e",
})
INK, INK2 = "#0b0b0b", "#52514e"
# One-hue sequential ramp (blue, light -> dark); colorblind-safe because it encodes magnitude by lightness.
SEQ = LinearSegmentedColormap.from_list("seq_blue", ["#f3f7fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
                                                     "#256abf", "#184f95", "#0d366b"])
CAT = {"paraphrase": ("#2a78d6", "o"), "keyword": ("#eb6834", "s")}  # categorical slots 1, 2 + marker shape

# ---- Study 1: frozen v2 files, selected explicitly by run --------------------------------------------------
V2_GROUPS = [
    # (label, file glob under results/v2, committed analysis markdown)
    ("Haiku 5.5", "2026-11-06_55325c9a_claude-haiku-5-5_v2_*.jsonl", "analysis.md"),
    ("Sonnet 5.5", "2026-11-06_9c37b82a_claude-sonnet-5-5_v2_*.jsonl", "analysis_sonnet.md"),
    ("Sonnet 5.5 rerun", "2026-11-06_3f64a2ee_claude-sonnet-5-5_v2_strict_explicit_rerun.jsonl",
     "analysis_sonnet_strict_explicit_rerun.md"),
]
V2_CONDS = ["solo", "solo@k5", "solo@k12", "pipeline", "swarm@n4", "swarm_noobj@n4", "relay_informed",
            "relay_uninformed"]
V2_COLS = [("none", "neutral"), ("none", "explicit"), ("strict", "neutral"), ("strict", "explicit")]
PROV_FILE = RES / "task-provenance" / "heldout-haiku.jsonl"
PROV_MD = RES / "task-provenance" / "heldout-haiku.jsonl.analysis.md"
PROV_CONDS = ["local", "provenance", "monitor", "keyword_gate"]
PROV_LABEL = {"local": "local", "provenance": "provenance", "monitor": "LLM monitor", "keyword_gate": "keyword gate"}

ID_COLS = ("model", "policy", "framing", "cond", "authorization")


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))


def fail(msg):
    sys.exit(f"make_figures: FAIL: {msg}")


def load_cells(paths):
    """Exactly analyze.main's path: load, drop pre-schema rows, enrich, summarize with the default identity."""
    raw = analyze.load_rows([str(p) for p in paths])
    raw = [r for r in raw if not is_preschema(r)]
    rows = [analyze.enrich(r) for r in raw]
    cells = analyze.summarize(rows, list(analyze.DEFAULT_BY))
    out = []
    for c in cells:
        key = dict(zip(analyze.DEFAULT_BY, c["key"]))
        if c["seed_clustered"]:
            fail(f"unexpected seed-clustered cell {key}")
        out.append({**c, "id": key})
    return out


def parse_md_cells(md_path):
    """Rows of the '## Cells' table of a committed analysis markdown, keyed by its identity columns."""
    lines = Path(md_path).read_text().splitlines()
    try:
        i = lines.index("## Cells")
    except ValueError:
        fail(f"no '## Cells' table in {rel(md_path)}")
    while not lines[i].startswith("|"):
        i += 1
    header = [h.strip() for h in lines[i].strip("|").split("|")]
    rows = []
    for line in lines[i + 2:]:
        if not line.startswith("|"):
            break
        vals = [v.strip() for v in line.strip("|").split("|")]
        row = dict(zip(header, vals))
        row["cond"] = row["cond"].rstrip("*")
        rows.append(row)
    return rows


def crosscheck(cell, md_rows, md_path):
    """Find the md row for this computed cell and require identical rendered rates and counts."""
    ids = cell["id"]
    hits = [r for r in md_rows if all(r[k] == str(ids.get(k)) for k in ID_COLS if k in r)]
    if len(hits) != 1:
        fail(f"{len(hits)} rows in {rel(md_path)} match computed cell {ids}")
    r = hits[0]
    checks = {"n_total": str(cell["n_total"]), "n_failed": str(cell["n_failed"]), "n_valid": str(cell["n_valid"]),
              "assembled": analyze._rate(cell["assembled"]), "recoverable": analyze._rate(cell["recoverable"])}
    for col, mine in checks.items():
        if r.get(col) != mine:
            fail(f"{rel(md_path)} {ids} column {col}: committed {r.get(col)!r} != recomputed {mine!r}")
    return r


def record(cell, endpoint, figure, panel, sources, md_path, md_row, extra=None):
    k, n, ci = cell[endpoint]
    lo, hi = cell[endpoint + "_all_bounds"]
    return {"figure": figure, "panel": panel, **{f: cell["id"].get(f) for f in ID_COLS},
            "run_id": cell["id"].get("run_id"), "endpoint": endpoint, "k": k, "n_valid": n,
            "n_total": cell["n_total"], "n_failed": cell["n_failed"], "proportion": k / n,
            "wilson95": [ci[0], ci[1]], "all_trial_range": [lo, hi], "source_files": sources,
            "crosscheck": {"file": rel(md_path), "committed_cell": md_row[endpoint],
                           "recomputed_cell": analyze._rate(cell[endpoint]), "match": True}, **(extra or {})}


def save(fig, stem):
    fig.savefig(OUT / f"{stem}.png", dpi=300, metadata={"Software": None})
    fig.savefig(OUT / f"{stem}.svg", metadata={"Date": None, "Creator": None})
    plt.close(fig)


# ---- Figure 2: v2 heatmap ------------------------------------------------------------------------------------
def v2_data():
    files = sorted((RES / "v2").glob("*.jsonl"))
    claimed, groups = set(), []
    for label, pattern, md in V2_GROUPS:
        paths = sorted((RES / "v2").glob(pattern))
        if not paths:
            fail(f"no v2 files for {pattern}")
        claimed.update(paths)
        manifests = {p: json.loads(Path(str(p) + ".manifest.json").read_text()) for p in paths}
        cells = load_cells(paths)
        md_path = RES / "v2" / md
        md_rows = parse_md_cells(md_path)
        if len(md_rows) != len(cells):
            fail(f"{rel(md_path)} has {len(md_rows)} cells, recomputed {len(cells)}")
        groups.append((label, paths, manifests, cells, md_path, md_rows))
    if set(files) != claimed:
        fail(f"unassigned v2 files: {sorted(rel(p) for p in set(files) - claimed)}")
    swarm_sizes = sorted({c["id"]["cond"].split("@n")[1] for g in groups for c in g[3] if "@n" in c["id"]["cond"]})
    return groups, swarm_sizes


def fig2(groups, records):
    # Columns per model: Haiku 4 cells; Sonnet 4 main cells + the verified-model strict/explicit rerun.
    panels = []
    for label, paths, manifests, cells, md_path, md_rows in groups:
        if label.endswith("rerun"):
            continue
        cols = [(label, pol, fr) for pol, fr in V2_COLS]
        if label.startswith("Sonnet"):
            cols.append(("Sonnet 5.5 rerun", "strict", "explicit"))
        panels.append((label, cols))
    by_group = {g[0]: g for g in groups}

    fig, axes = plt.subplots(2, 2, figsize=(7.4, 8.6), gridspec_kw={"hspace": 0.5, "wspace": 0.06})
    for r, (model_label, cols) in enumerate(panels):
        for c, endpoint in enumerate(("assembled", "recoverable")):
            ax = axes[r, c]
            ax.set_xlim(-0.5, 4.5)  # same cell width in every panel; Haiku has no rerun column
            ax.set_ylim(len(V2_CONDS) - 0.5, -0.5)
            xt = []
            for j, (glabel, pol, fr) in enumerate(cols):
                label, paths, manifests, cells, md_path, md_rows = by_group[glabel]
                path = next(p for p in paths if p.name.endswith(f"_{pol}_{fr}.jsonl") or
                            p.name.endswith(f"_{pol}_{fr}_rerun.jsonl"))
                served = manifests[path].get("resolved_model") or []
                mixed = len(served) > 1
                rerun = glabel.endswith("rerun")
                xt.append(f"{pol}\n{fr}" + ("\nrerun" if rerun else "") + ("†" if mixed else ""))
                for i, cond in enumerate(V2_CONDS):
                    hits = [x for x in cells if x["id"]["cond"] == cond and x["id"]["policy"] == pol
                            and x["id"]["framing"] == fr]
                    if len(hits) != 1:
                        fail(f"{glabel} {pol}/{fr}/{cond}: {len(hits)} cells")
                    cell = hits[0]
                    md_row = crosscheck(cell, md_rows, md_path)
                    k, n, _ = cell[endpoint]
                    p = k / n
                    ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=SEQ(p), edgecolor="white", lw=2))
                    ax.text(j, i, f"{k}/{n}", ha="center", va="center", fontsize=9,
                            color="white" if p >= 0.5 else INK)
                    records.append(record(cell, endpoint, "fig2_v2_heatmap", f"{model_label} / {endpoint}",
                                          [rel(path)], md_path, md_row,
                                          {"model_label": glabel, "served_models_manifest": served,
                                           "mixed_served_models": mixed}))
            ax.set_xticks(range(len(cols)), xt)
            ax.xaxis.tick_top()
            ax.tick_params(length=0)
            ax.set_yticks(range(len(V2_CONDS)), V2_CONDS if c == 0 else [])
            for s in ax.spines.values():
                s.set_visible(False)
            n_seeds = {x["n_valid"] for x in by_group[model_label][3]}
            header_lines = max(t.count("\n") + 1 for t in xt)
            ax.set_title(f"{model_label}: {endpoint} (n = {'/'.join(map(str, sorted(n_seeds)))}/cell)",
                         loc="left", pad=6 + 12 * header_lines, color=INK)
    sm = plt.cm.ScalarMappable(cmap=SEQ, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, ax=axes, orientation="horizontal", fraction=0.022, pad=0.03, aspect=50)
    cb.set_label("share of valid runs (cell text: k/n)", color=INK)
    cb.outline.set_visible(False)
    note = ("Study 1 (v2, held-out seeds). Columns: policy (none/strict, same for every role) x framing "
            "(neutral/explicit). Relay prompts do not use framing, so relay framing cells are replicates. "
            "† Run manifest lists two served models (claude-sonnet-5, claude-sonnet-5-5); the rerun on the "
            "same 10 seeds was served by claude-sonnet-5-5 only.")
    fig.text(0.02, 0.005, textwrap.fill(note, 125, break_on_hyphens=False), fontsize=8, color=INK2, va="bottom")
    fig.subplots_adjust(left=0.19, right=0.99, top=0.91, bottom=0.16)
    save(fig, "fig2_v2_heatmap")


# ---- Figure 4: Study 2 held-out provenance --------------------------------------------------------------------
def fig4(records):
    cells = load_cells([PROV_FILE])
    md_rows = parse_md_cells(PROV_MD)
    if len(md_rows) != len(cells):
        fail(f"{rel(PROV_MD)} has {len(md_rows)} cells, recomputed {len(cells)}")
    panels = [("restricted", "recoverable", "Restricted objective: recoverable\n(disclosure; lower is safer)"),
              ("authorized", "assembled", "Authorized objective: assembled\n(utility; higher is better)")]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.9), sharey=True, gridspec_kw={"wspace": 0.12})
    notes = []
    for ax, (auth, endpoint, title) in zip(axes, panels):
        for i, cond in enumerate(PROV_CONDS):
            for d, wording in ((-0.17, "paraphrase"), (0.17, "keyword")):
                hits = [x for x in cells if x["id"]["cond"] == cond and x["id"]["authorization"] == auth
                        and x["id"]["framing"] == wording]
                if len(hits) != 1:
                    fail(f"provenance {auth}/{wording}/{cond}: {len(hits)} cells")
                cell = hits[0]
                md_row = crosscheck(cell, md_rows, PROV_MD)
                k, n, (lo, hi) = cell[endpoint]
                p, y = k / n, i + d
                color, marker = CAT[wording]
                ax.plot([lo, hi], [y, y], color=color, lw=2, solid_capstyle="round")
                ax.plot([p], [y], marker=marker, ms=7, color=color, mec="white", mew=1.5, ls="none")
                lab = f"{k}/{n}"
                if cell["n_failed"]:
                    lab += "*"
                    a_lo, a_hi = cell[endpoint + "_all_bounds"]
                    notes.append(f"* {cell['n_failed']} trial failed (backend error) in {wording} / {auth} / {cond}; "
                                 f"excluded, valid n = {n}; all-trial range {a_lo:.0%}-{a_hi:.0%}.")
                if hi < 0.8:
                    ax.text(hi + 0.025, y, lab, va="center", ha="left", fontsize=9, color=INK)
                else:
                    ax.text(lo - 0.025, y, lab, va="center", ha="right", fontsize=9, color=INK)
                records.append(record(cell, endpoint, "fig4_provenance_heldout", f"{auth} / {endpoint}",
                                      [rel(PROV_FILE)], PROV_MD, md_row))
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(len(PROV_CONDS) - 0.5, -0.5)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"])
        ax.grid(axis="x", color="#e4e3df", lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_title(title, loc="left", color=INK)
        ax.set_xlabel("share of valid trials (Wilson 95% CI)")
    axes[0].set_yticks(range(len(PROV_CONDS)), [PROV_LABEL[c] for c in PROV_CONDS])
    handles = [plt.Line2D([], [], color=CAT[w][0], marker=CAT[w][1], ms=7, mec="white", mew=1.5, lw=2,
                          label=f"{w} wording") for w in ("paraphrase", "keyword")]
    fig.legend(handles=handles, loc="upper right", ncol=2, frameon=False, bbox_to_anchor=(0.99, 1.0))
    fig.text(0.02, 0.01, "Study 2 (task provenance, held-out seeds 3000-3049, Claude Haiku 5.5, 50 seeds per cell); "
             "not pooled with Study 1.\n" + "\n".join(dict.fromkeys(notes)), fontsize=8, color=INK2, va="bottom")
    fig.subplots_adjust(left=0.14, right=0.98, top=0.82, bottom=0.27)
    save(fig, "fig4_provenance_heldout")


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=OUT, help="output directory (default: report/figures)")
    OUT = parser.parse_args().out_dir.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    groups, swarm_sizes = v2_data()
    # Cross-check every committed cell of both studies before any file is written.
    n_checked = 0
    for _, _, _, cells, md_path, md_rows in groups:
        for cell in cells:
            crosscheck(cell, md_rows, md_path)
            n_checked += 1
    prov_rows = parse_md_cells(PROV_MD)
    for cell in load_cells([PROV_FILE]):
        crosscheck(cell, prov_rows, PROV_MD)
        n_checked += 1
    fig2(groups, records)
    skipped = {}
    if len(swarm_sizes) < 2:
        skipped["fig3_v2_swarm_size"] = (f"frozen v2 data contain a single swarm size (n = {', '.join(swarm_sizes)}); "
                                         "no outcome-vs-size relation can be plotted without new runs")
    else:  # pragma: no cover - would need new frozen data and a figure design
        fail(f"multiple swarm sizes {swarm_sizes} found; fig3 not implemented")
    fig4(records)
    data = {
        "generator": "report/figures/make_figures.py",
        "command": "uv run --no-project --with matplotlib python report/figures/make_figures.py",
        "scoring": "experiments/composition-gap/analyze.py summarize() over scoring.score_row(); valid rows only; "
                   "Wilson 95% intervals",
        "studies_pooled": False,
        "skipped": skipped,
        "crosscheck": f"all {n_checked} committed cells ({len(records)} plotted values) reproduce the committed "
                      "analysis markdown exactly (k/n, rounded percent, rounded Wilson CI, n_total, n_failed, n_valid)",
        "values": records,
    }
    (OUT / "figure-data.json").write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    for name, why in skipped.items():
        print(f"skipped {name}: {why}")
    print(f"cross-checked {n_checked} committed cells OK; wrote fig2_v2_heatmap, fig4_provenance_heldout "
          f"(png+svg) and figure-data.json ({len(records)} plotted values)")


if __name__ == "__main__":
    main()
