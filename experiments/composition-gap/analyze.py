"""Cell summaries and seed-paired contrasts for composition-gap result files.

  python analyze.py FILE.jsonl [FILE...] [--md OUT.md] [--by model,policy,framing,cond]
                    [--baseline solo] [--include-superseded] [--include-unknown] [--legacy-check]

Denominators: only VALID rows (failed_calls == 0) count. Rows with failed_calls > 0 are "failed" and rows
without the field are "unknown"; both are reported separately. --include-unknown treats unknown rows as valid
(needed for early pilots that predate failure tracking; n_unknown is still shown).
Stdlib only; bootstrap RNG is seeded so output is reproducible.
"""
import argparse, json, math, random, sys
from collections import defaultdict

from scoring import score_row, is_preschema

Z = 1.959964
B = 2000
BOOT_SEED = 20261106


def wilson(k, n, z=Z):
    """Wilson score interval for k successes in n trials; None if n == 0."""
    if n == 0:
        return None
    p, z2 = k / n, z * z
    d = 1 + z2 / n
    c = (p + z2 / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def boot_ci(clusters, b=B, seed=BOOT_SEED):
    """95% percentile CI for the pooled mean of values grouped in clusters (list of lists); resamples whole
    clusters (seeds) with replacement. None if no data."""
    clusters = [c for c in clusters if c]
    if not clusters:
        return None
    rng = random.Random(seed)
    k = len(clusters)
    means = []
    for _ in range(b):
        tot = cnt = 0
        for _ in range(k):
            c = clusters[rng.randrange(k)]
            tot += sum(c); cnt += len(c)
        means.append(tot / cnt)
    means.sort()
    return means[int(0.025 * b)], means[min(b - 1, int(0.975 * b))]


def mcnemar_p(b, c):
    """Exact two-sided binomial p for discordant counts b, c (H0: p=0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def load_rows(paths, include_superseded=False):
    rows = []
    for p in paths:
        if "/superseded/" in p.replace("\\", "/") and not include_superseded:
            print(f"WARNING: skipping superseded file {p} (use --include-superseded)", file=sys.stderr)
            continue
        with open(p) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    r["_file"] = p
                    rows.append(r)
    return rows


def enrich(row):
    s = score_row(row)
    keep = {k: row.get(k) for k in ("cond", "seed", "model", "policy", "framing", "backend", "design", "run_id", "_file")}
    return {**keep, **s, "_raw": row}


def is_valid(r, include_unknown):
    return r["valid"] is True or (include_unknown and r["valid"] == "unknown")


def cell_key(r, by):
    return tuple(str(r.get(k)) if r.get(k) is not None else "-" for k in by)


def summarize(rows, by, include_unknown=False):
    cells = defaultdict(list)
    for r in rows:
        cells[cell_key(r, by)].append(r)
    out = []
    for key in sorted(cells):
        rs = cells[key]
        v = [r for r in rs if is_valid(r, include_unknown)]
        n = len(v)
        cell = {"key": key, "n_total": len(rs), "n_failed": sum(r["valid"] is False for r in rs),
                "n_unknown": sum(r["valid"] == "unknown" for r in rs), "n_valid": n}
        for m in ("assembled", "recoverable"):
            k = sum(bool(r[m]) for r in v)
            cell[m] = (k, n, wilson(k, n))
        for m in ("identified_parts", "exposed_parts"):
            by_seed = defaultdict(list)
            for r in v:
                by_seed[r["seed"]].append(r[m])
            cell[m] = (sum(r[m] for r in v) / n if n else None, boot_ci(list(by_seed.values())))
        out.append(cell)
    return out


def paired_contrasts(rows, baseline="solo", include_unknown=False):
    """Seed-paired contrasts of every non-baseline cond vs baseline within (model, policy, framing).
    One row per (cell, seed) is used (the first valid one)."""
    groups = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        if is_valid(r, include_unknown):
            groups[cell_key(r, ("model", "policy", "framing"))][r["cond"]].setdefault(r["seed"], r)
    out = []
    for g in sorted(groups):
        conds = groups[g]
        if baseline not in conds:
            continue
        for c in sorted(conds):
            if c == baseline:
                continue
            seeds = sorted(set(conds[c]) & set(conds[baseline]))
            if not seeds:
                continue
            res = {"group": g, "cond": c, "n_pairs": len(seeds)}
            for m in ("assembled", "recoverable", "identified_parts"):
                d = [float(conds[c][s][m]) - float(conds[baseline][s][m]) for s in seeds]
                res[m] = (sum(d) / len(d), boot_ci([[x] for x in d]))
                if m != "identified_parts":
                    bb = sum(x > 0 for x in d); cc = sum(x < 0 for x in d)
                    res[m + "_disc"] = (bb, cc, mcnemar_p(bb, cc))
            out.append(res)
    return out


def legacy_check(rows):
    """Compare recomputed legacy metrics with stored ones, and list rows where new metrics disagree."""
    have = [r for r in rows if "joined" in r["_raw"]]
    ok = [r for r in have if r["legacy_joined"] == r["_raw"]["joined"]
          and r["legacy_parts"] == r["_raw"]["parts_disclosed"]
          and r["legacy_all"] == r["_raw"]["all_disclosed"]]
    bad = [r for r in have if r not in ok]
    asm_ne = [r for r in have if r["assembled"] != r["_raw"]["joined"]]
    ident_lt = [r for r in have if r["identified_parts"] < r["_raw"]["parts_disclosed"]]
    ident_gt = [r for r in have if r["identified_parts"] > r["_raw"]["parts_disclosed"]]
    return {"n_stored": len(have), "n_reproduced": len(ok), "mismatch": bad, "assembled_ne_joined": asm_ne,
            "identified_lt_legacy": ident_lt, "identified_gt_legacy": ident_gt}


def _ci(ci, pct=True):
    if ci is None:
        return "n/a"
    return f"{ci[0] * 100:.0f}-{ci[1] * 100:.0f}%" if pct else f"{ci[0]:.2f} to {ci[1]:.2f}"


def _rate(t):
    k, n, ci = t
    return f"{k}/{n} ({k / n * 100:.0f}%) [{_ci(ci)}]" if n else "n/a"


def _mean(t):
    m, ci = t
    return "n/a" if m is None else f"{m:.2f} [{_ci(ci, False)}]"


def _signed(t, pct):
    m, ci = t
    if pct:
        return f"{m * 100:+.0f}pp [{ci[0] * 100:+.0f}, {ci[1] * 100:+.0f}]"
    return f"{m:+.2f} [{ci[0]:+.2f}, {ci[1]:+.2f}]"


def _disc(t):
    return f"+{t[0]}/-{t[1]}, p={t[2]:.3f}"


def render(rows, by, baseline, include_unknown, files_note="", check=False):
    def vals(k):
        return sorted({str(r.get(k)) for r in rows if r.get(k) is not None}) or ["(none)"]
    L = ["# Composition-gap analysis", "",
         "**Exploratory: pilot data, tiny n. Intervals are descriptive; nothing here is confirmatory.**", ""]
    if files_note:
        L += [files_note, ""]
    L += [f"- designs: {', '.join(vals('design'))}", f"- run_ids: {', '.join(vals('run_id'))}",
          f"- backends: {', '.join(vals('backend'))}", f"- models: {', '.join(vals('model'))}",
          f"- rows: {len(rows)}; unknown-validity rows {'treated as valid' if include_unknown else 'excluded from denominators'}"
          " (reported in n_unknown)",
          "- CIs: Wilson 95% for proportions; seed-bootstrap 95% (2000 resamples, seeded) for means; "
          "metrics from posted messages only (see scoring.py)", ""]
    L += ["## Cells", "",
          "| " + " | ".join(by) + " | n_total | n_failed | n_unknown | n_valid | assembled | recoverable | mean identified | mean exposed |",
          "|" + "---|" * (len(by) + 8)]
    for c in summarize(rows, by, include_unknown):
        L.append("| " + " | ".join(c["key"]) + f" | {c['n_total']} | {c['n_failed']} | {c['n_unknown']} | {c['n_valid']} | "
                 f"{_rate(c['assembled'])} | {_rate(c['recoverable'])} | {_mean(c['identified_parts'])} | {_mean(c['exposed_parts'])} |")
    pc = paired_contrasts(rows, baseline, include_unknown)
    L += ["", f"## Seed-paired contrasts vs `{baseline}`", "",
          "Difference = cond minus baseline, paired by seed within (model, policy, framing); brackets are paired-bootstrap 95% CIs. "
          "Discordant: +b = cond succeeded where baseline did not, -c = the reverse; p is the exact two-sided binomial (McNemar) test.", ""]
    if not pc:
        L.append(f"(no pairs: baseline `{baseline}` absent or no valid shared seeds)")
    else:
        L += ["| model/policy/framing | cond | pairs | d assembled | discordant | d recoverable | discordant | d identified |",
              "|---|---|---|---|---|---|---|---|"]
        for p in pc:
            L.append(f"| {'/'.join(p['group'])} | {p['cond']} | {p['n_pairs']} | {_signed(p['assembled'], True)} | {_disc(p['assembled_disc'])} | "
                     f"{_signed(p['recoverable'], True)} | {_disc(p['recoverable_disc'])} | {_signed(p['identified_parts'], False)} |")
    if check:
        k = legacy_check(rows)
        L += ["", "## Legacy reproduction and disagreements", "",
              f"- Rows with stored legacy fields: {k['n_stored']}; recomputed legacy joined/parts/all reproduce them exactly for {k['n_reproduced']}.",
              f"- Mismatches: {len(k['mismatch'])}",
              f"- Rows where new `assembled` != stored `joined`: {len(k['assembled_ne_joined'])}",
              f"- Rows where `identified_parts` < stored `parts_disclosed`: {len(k['identified_lt_legacy'])}",
              f"- Rows where `identified_parts` > stored `parts_disclosed`: {len(k['identified_gt_legacy'])}"]
        for name, lst in (("assembled != joined", k["assembled_ne_joined"]), ("identified < legacy parts", k["identified_lt_legacy"]),
                          ("identified > legacy parts", k["identified_gt_legacy"]), ("legacy mismatch", k["mismatch"])):
            if lst:
                L += ["", f"{name}:", "", "| file | cond | seed | stored joined/parts | assembled | identified | exposed |", "|---|---|---|---|---|---|---|"]
                for r in lst:
                    f = r["_file"].split("/")[-1]
                    L.append(f"| {f} | {r['cond']} | {r['seed']} | {r['_raw']['joined']}/{r['_raw']['parts_disclosed']} | "
                             f"{r['assembled']} | {r['identified_parts']} | {r['exposed_parts']} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--md")
    ap.add_argument("--by", default="model,policy,framing,cond")
    ap.add_argument("--baseline", default="solo")
    ap.add_argument("--include-superseded", action="store_true")
    ap.add_argument("--include-unknown", action="store_true", help="count rows lacking failed_calls as valid")
    ap.add_argument("--legacy-check", action="store_true")
    a = ap.parse_args(argv)
    raw = load_rows(a.files, a.include_superseded)
    pre = [r for r in raw if is_preschema(r)]
    raw = [r for r in raw if not is_preschema(r)]
    rows = [enrich(r) for r in raw]
    note = "Files: " + ", ".join(sorted({r["_file"].split("/")[-1] for r in rows}))
    if pre:
        note += (f"\n\nExcluded {len(pre)} pre-schema row(s) ({', '.join(sorted({r['_file'].split('/')[-1] for r in pre}))}): "
                 "they predate the frozen task generator, so their words do not match make_task(seed) and cannot be scored.")
        print(f"WARNING: excluded {len(pre)} pre-schema rows", file=sys.stderr)
    out = render(rows, a.by.split(","), a.baseline, a.include_unknown, note, a.legacy_check)
    print(out)
    if a.md:
        with open(a.md, "w") as f:
            f.write(out)


if __name__ == "__main__":
    main()
