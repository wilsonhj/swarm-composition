"""Cell summaries and seed-paired contrasts for composition-gap result files.

  python analyze.py FILE.jsonl [FILE...] [--md OUT.md] [--by model,policy,framing,cond]
                    [--baseline matched|solo|COND] [--include-superseded] [--include-unknown] [--legacy-check]

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
# Runs are independent replications. Pair only within a compatible run; old rows
# without provenance retain explicit missing values rather than borrowing metadata.
# Served models come from per-row turn logs (a fully failed trial logs none), so they are
# reported as cell metadata, not identity: they must not split a run's cells or pairs.
IDENTITY = ("study", "design", "backend", "model", "authorization", "policy", "framing",
            "run_id", "prompt_hash", "protocol_hash")
DEFAULT_BY = (*IDENTITY, "cond")


def validate_rows(rows, by=None):
    """Reject repeated trials and summary groups that would merge incompatible runs."""
    seen, groups = set(), defaultdict(set)
    for r in rows:
        identity = cell_key(r, IDENTITY)
        trial = (identity, r.get("cond"), r.get("seed"))
        if trial in seen:
            raise ValueError(f"duplicate trial: condition={r.get('cond')}, seed={r.get('seed')}, "
                             f"run_id={r.get('run_id')}; select one input copy/run")
        seen.add(trial)
        if by is not None:
            groups[cell_key(r, by)].add(identity)
    if any(len(g) > 1 for g in groups.values()):
        raise ValueError("--by would merge incompatible study/design/backend/run metadata; "
                         "retain the default grouping or select one run")


def matched_baseline(cond):
    if cond == "pipeline": return "solo@k5"
    if cond.startswith("relay"): return "solo@k6"
    if cond.startswith(("swarm@n", "swarm_noobj@n")):
        return f"solo@k{3 * int(cond.rsplit('@n', 1)[1])}"
    return None


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
    keep = {k: row.get(k) for k in (*IDENTITY, "cond", "seed", "_file")}
    served = set()
    for turn in row.get("turns") or []:
        model = turn.get("model")
        if isinstance(model, str): served.add(model)
        elif isinstance(model, list): served.update(model)
    if served: keep["served_models"] = ",".join(sorted(served))
    return {**keep, **s, "_raw": row}


def is_valid(r, include_unknown):
    return r["valid"] is True or (include_unknown and r["valid"] == "unknown")


def cell_key(r, by):
    return tuple(str(r.get(k)) if r.get(k) is not None else "-" for k in by)


def summarize(rows, by, include_unknown=False, validate=True):
    if validate: validate_rows(rows, by)
    cells = defaultdict(list)
    for r in rows:
        cells[cell_key(r, by)].append(r)
    out = []
    for key in sorted(cells):
        rs = cells[key]
        v = [r for r in rs if is_valid(r, include_unknown)]
        n = len(v)
        cell = {"key": key, "n_total": len(rs), "n_failed": sum(r["valid"] is False for r in rs),
                "n_unknown": sum(r["valid"] == "unknown" for r in rs), "n_valid": n,
                "served_models": sorted({m for r in rs if r.get("served_models") for m in r["served_models"].split(",")})}
        for m in ("assembled", "recoverable"):
            k = sum(bool(r[m]) for r in v)
            cell[m] = (k, n, wilson(k, n))
            cell[m + "_all_bounds"] = (k / len(rs), (k + len(rs) - n) / len(rs))
        for m in ("identified_parts", "exposed_parts"):
            by_seed = defaultdict(list)
            for r in v:
                by_seed[r["seed"]].append(r[m])
            cell[m] = (sum(r[m] for r in v) / n if n else None, boot_ci(list(by_seed.values())))
        out.append(cell)
    return out


def paired_contrasts(rows, baseline="solo", include_unknown=False, validate=True, skipped=None):
    """Seed-paired contrasts within compatible runs; never silently pick a duplicate.
    `matched` selects call-budget baselines for v2 topologies, skipping absent baselines;
    pass a list as `skipped` to collect the conditions omitted that way."""
    if validate: validate_rows(rows)
    groups = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        if is_valid(r, include_unknown):
            groups[cell_key(r, IDENTITY)][r["cond"]][r["seed"]] = r
    out = []
    for g in sorted(groups):
        conds = groups[g]
        for c in sorted(conds):
            reference = matched_baseline(c) if baseline == "matched" else baseline
            if not reference or c == reference:
                continue
            seeds = sorted(set(conds[c]) & set(conds.get(reference, ())))
            if not seeds:
                if baseline == "matched" and skipped is not None:
                    skipped.append({"group": g, "cond": c, "baseline": reference})
                continue
            res = {"group": g, "cond": c, "baseline": reference, "n_pairs": len(seeds)}
            for m in ("assembled", "recoverable", "identified_parts"):
                d = [float(conds[c][s][m]) - float(conds[reference][s][m]) for s in seeds]
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
    validate_rows(rows, by)
    def vals(k):
        return sorted({str(r.get(k)) for r in rows if r.get(k) is not None}) or ["(none)"]
    L = ["# Composition-gap analysis", "",
         "**Descriptive analysis. Design and seed labels alone do not verify prospective freezing or held-out status.**",
         "Interpret against the committed protocol and run manifests; primary comparisons must be specified before collection.", ""]
    if any(r.get("backend") == "mock" for r in rows):
        L += ["**MOCK DATA: scripted software checks, not empirical model evidence.**", ""]
    if files_note:
        L += [files_note, ""]
    nf = sum(r.get("valid") is False for r in rows)
    L += [f"- designs: {', '.join(vals('design'))}", f"- run_ids: {', '.join(vals('run_id'))}",
          f"- backends: {', '.join(vals('backend'))}", f"- models: {', '.join(vals('model'))}",
          f"- failed rows excluded (failed_calls>0): {nf}/{len(rows)}; duplicate trial keys rejected",
          f"- rows: {len(rows)}; unknown-validity rows {'treated as valid' if include_unknown else 'excluded from denominators'}"
          " (reported in n_unknown)",
          "- CIs: Wilson 95% for proportions; seed-bootstrap 95% (2000 resamples, seeded) for means; "
          "metrics from posted messages only (see scoring.py)", ""]
    # Keep full identities for grouping, but avoid repeating constant metadata and
    # 64-character hashes in every cell. Full values remain in the metadata above/below.
    display_by = [k for k in by if k == "cond" or len({r.get(k) for r in rows}) > 1] or list(by)
    indices = [by.index(k) for k in display_by]
    def compact(value): return value[:12] if len(value) > 32 else value
    def display_key(key): return " | ".join(compact(key[i]) for i in indices)
    def run_label(group):
        return ", ".join(f"{field}={compact(group[i])}" for i, field in enumerate(IDENTITY)
                         if len({r.get(field) for r in rows}) > 1) or "single run"
    def served(models): return (",".join(models) + (" (MIXED)" if len(models) > 1 else "")) if models else "-"
    show_served = any(r.get("served_models") for r in rows)
    served_header = " | served models" if show_served else ""
    for k in ("study", "served_models", "authorization", "prompt_hash", "protocol_hash"):
        L.append(f"- {k}: {', '.join(vals(k))}")
    failures = any(not is_valid(r, include_unknown) for r in rows)
    bounds_header = " | assembled all-trial range | recoverable all-trial range" if failures else ""
    L += ["", "## Cells", "",
          "| " + " | ".join(display_by) + " | n_total | n_failed | n_unknown | n_valid | assembled | recoverable | mean identified | mean exposed" + bounds_header + served_header + " |",
          "|" + "---|" * (len(display_by) + 8 + (2 if failures else 0) + show_served)]
    for c in summarize(rows, by, include_unknown, validate=False):
        bounds = (f" | {_ci(c['assembled_all_bounds'])} | {_ci(c['recoverable_all_bounds'])}" if failures else "")
        L.append("| " + display_key(c["key"]) + f" | {c['n_total']} | {c['n_failed']} | {c['n_unknown']} | {c['n_valid']} | "
                 f"{_rate(c['assembled'])} | {_rate(c['recoverable'])} | {_mean(c['identified_parts'])} | {_mean(c['exposed_parts'])}" + bounds
                 + (f" | {served(c['served_models'])}" if show_served else "") + " |")
    if show_served:
        L += ["", "Served models: union of the cell's per-turn logs (`-`: none logged); MIXED marks more than one. "
              "They do not split cells: fully failed trials log none and stay in their run's cell."]
    if failures:
        L += ["", "All-trial ranges assign every excluded failed/unknown trial first failure, then success. "
              "They are sensitivity bounds, not confidence intervals; valid-only rates may be selection-biased."]
    relay = [r for r in rows if str(r.get("cond", "")).startswith("relay") and is_valid(r, include_unknown)]
    if relay:
        L += ["", "## Relay coordinator requests", "",
              "From `scoring.relay_request` (coordinator's first turn posted). Relay prompts do not use `framing`, so "
              "framing cells are replicates for relay.", "",
              "| " + " | ".join(display_by) + " | n_valid | requested | request names secret |", "|" + "---|" * (len(display_by) + 3)]
        groups = {}
        for r in relay:
            groups.setdefault(cell_key(r, by), []).append(r)
        for k in sorted(groups):
            g = groups[k]; n = len(g)
            req = sum(bool(r.get("requested")) for r in g); sec = sum(bool(r.get("request_names_secret")) for r in g)
            L.append("| " + display_key(k) + f" | {n} | {_rate((req, n, wilson(req, n)))} | {_rate((sec, n, wilson(sec, n)))} |")
    skipped = []
    pc = paired_contrasts(rows, baseline, include_unknown, validate=False, skipped=skipped)
    title = "matched call-budget baselines" if baseline == "matched" else f"`{baseline}`"
    L += ["", f"## Seed-paired contrasts vs {title}", "",
          "Difference = cond minus baseline, paired by seed within compatible study/design/backend/run metadata; brackets are paired-bootstrap 95% CIs. "
          "Discordant: +b = cond succeeded where baseline did not, -c = the reverse; p is the exact two-sided binomial (McNemar) test.", ""]
    if not pc and baseline == "matched":
        L.append("(no pairs: no condition has its matched call-budget baseline with valid shared seeds)")
    elif not pc:
        L.append(f"(no pairs: baseline condition `{baseline}` absent or no valid shared seeds)")
    else:
        L += ["| varying run metadata | cond | baseline | pairs | d assembled | discordant | d recoverable | discordant | d identified |",
              "|---|---|---|---|---|---|---|---|---|"]
        for p in pc:
            L.append(f"| {run_label(p['group'])} | {p['cond']} | {p['baseline']} | {p['n_pairs']} | {_signed(p['assembled'], True)} | {_disc(p['assembled_disc'])} | "
                     f"{_signed(p['recoverable'], True)} | {_disc(p['recoverable_disc'])} | {_signed(p['identified_parts'], False)} |")
    if baseline == "matched":
        L += ["", "Matched call budgets: pipeline→solo@k5; relay→solo@k6; swarm@nN→solo@k(3N). "
              "Groups lacking the reference are omitted, not compared to one-attempt solo. Swarm matching uses its maximum turns."]
        if skipped:
            L += ["", "Omitted (matched baseline absent or no valid shared seeds):", "",
                  "| varying run metadata | cond | missing baseline |", "|---|---|---|"]
            L += [f"| {run_label(s['group'])} | {s['cond']} | {s['baseline']} |" for s in skipped]
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
    ap.add_argument("--by", default=",".join(DEFAULT_BY))
    ap.add_argument("--baseline", default="matched", help="matched (default), solo, or a named condition")
    ap.add_argument("--include-superseded", action="store_true")
    ap.add_argument("--include-unknown", action="store_true", help="count rows lacking failed_calls as valid")
    ap.add_argument("--legacy-check", action="store_true")
    ap.add_argument("--run-id", action="append", help="select one or more run IDs before grouping")
    a = ap.parse_args(argv)
    raw = load_rows(a.files, a.include_superseded)
    if a.run_id:
        raw = [r for r in raw if r.get("run_id") in a.run_id]
        if not raw: ap.error("no rows match --run-id")
    pre = [r for r in raw if is_preschema(r)]
    raw = [r for r in raw if not is_preschema(r)]
    rows = [enrich(r) for r in raw]
    note = "Files: " + ", ".join(sorted({r["_file"].split("/")[-1] for r in rows}))
    if pre:
        note += (f"\n\nExcluded {len(pre)} pre-schema row(s) ({', '.join(sorted({r['_file'].split('/')[-1] for r in pre}))}): "
                 "they predate the frozen task generator, so their words do not match make_task(seed) and cannot be scored.")
        print(f"WARNING: excluded {len(pre)} pre-schema rows", file=sys.stderr)
    try:
        out = render(rows, a.by.split(","), a.baseline, a.include_unknown, note, a.legacy_check)
    except ValueError as e:
        ap.error(str(e))
    print(out)
    if a.md:
        with open(a.md, "w") as f:
            f.write(out)


if __name__ == "__main__":
    main()
