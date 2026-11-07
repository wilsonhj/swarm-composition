#!/usr/bin/env python3
"""Replay the pinned task-provenance held-out run (Haiku 5.5) offline.

Verifies archived artifacts against provenance-inputs.json, re-executes every
trial's protocol logic from its logged replies, rescores all rows, reconciles
counts with the manifest, and regenerates the analysis with both the analyzer
that produced the committed report and the snapshot analyzer. No model calls,
network or credentials; Python's standard library and git only.
"""
import argparse
import hashlib
import importlib
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile

CONTRACT_PATH = pathlib.Path(__file__).resolve().parents[1] / "provenance-inputs.json"
MODULES = ("analyze", "scoring", "harness", "provenance")
# Added to each row by provenance.main after run_trial returns.
RUN_METADATA = ("run_id", "backend", "model", "phase", "prompt_hash", "protocol_hash")
PAIRED_COUNTS = "paired counts (both/b/c/neither)"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def git(repo, *args, binary=False):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=not binary,
                                   stderr=subprocess.DEVNULL)


def run_analyzer(src, raw, out_md):
    """Run analyze.py from `src` only (isolated mode: no cwd, script dir, env or user site)."""
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import analyze; "
            "analyze.main([sys.argv[2], '--baseline', 'local', '--md', sys.argv[3]])")
    p = subprocess.run([sys.executable, "-I", "-c", code, str(src), str(raw), str(out_md)],
                       capture_output=True, text=True)
    require(p.returncode == 0 and not p.stderr.strip(),
            f"Analyzer from {src.name} failed or warned: {p.stderr.strip()}")
    return out_md.read_bytes()


def table_cells(line):
    return line.strip().strip("|").split("|")


def compare_reports(committed, regenerated):
    """Allow only the documented additive differences of the newer analyzer."""
    old, new = committed.splitlines(), regenerated.splitlines()
    require(len(old) == len(new), "Snapshot report line count differs from committed report")
    header = next((l for l in new if PAIRED_COUNTS in l), None)
    require(header is not None, "Snapshot report lacks the paired-count columns")
    drop = {i for i, c in enumerate(table_cells(header)) if c.strip() == PAIRED_COUNTS}
    changed = [i for i, (a, b) in enumerate(zip(old, new)) if a != b]
    for i in changed:
        a, b = old[i], new[i]
        if a.startswith("Difference = cond minus baseline"):
            missing = [s for s in a.split(". ") if s.rstrip(".") not in b]
            require(not missing, f"Contrast note lost text: {missing}")
        else:
            kept = [c for j, c in enumerate(table_cells(b)) if j not in drop]
            require(a.startswith("|") and kept == table_cells(a),
                    f"Snapshot report differs beyond added paired-count columns at line {i + 1}")
    return {"lines": len(old), "changed_lines": len(changed),
            "dropped_columns": sorted(drop), "other_lines_identical": True}


def replay(repo, contract, contract_path, out, work):
    exp = contract["expected"]
    snap, coll, data = work / "snapshot", work / "collection", work / "data"
    for d in (snap, coll, data):
        d.mkdir()
    blobs = {}
    for item in contract["files"]:
        path = repo / item["path"]
        require(path.is_file(), f"Missing input: {item['path']}")
        blob = path.read_bytes()
        require(sha(blob) == item["sha256"], f"SHA256 mismatch: {item['path']}")
        blobs[item["kind"]] = blobs.get(item["kind"], []) + [(path.name, blob)]
        # Analyze copies of the verified bytes only, so neither later edits nor
        # untracked files beside the originals can change what is analyzed or imported.
        if item["kind"] == "analysis_source":
            (snap / path.name).write_bytes(blob)
        elif item["kind"] == "raw":
            raw_path = data / path.name
            raw_path.write_bytes(blob)
    (_, manifest_blob), = blobs["manifest"]
    (_, log_blob), = blobs["log"]
    (_, committed), = blobs["committed_analysis"]
    (_, protocol), = blobs["protocol"]

    # Sources that produced the committed analysis, read from git history and hash-checked.
    source = contract["collection_sources"]
    for item in source["files"]:
        try:
            blob = git(repo, "show", f"{source['commit']}:{item['path']}", binary=True)
        except subprocess.CalledProcessError:
            raise ValueError(f"Cannot read {item['path']} at {source['commit']}; "
                             "use a checkout with full history") from None
        require(sha(blob) == item["sha256"], f"SHA256 mismatch: {item['path']} at {source['commit']}")
        if item["path"].endswith(".py"):
            (coll / pathlib.PurePosixPath(item["path"]).name).write_bytes(blob)
    commit = git(repo, "rev-parse", "HEAD").strip()
    tracked_changes = git(repo, "status", "--porcelain", "--untracked-files=no")
    freeze = contract["freeze_commit"]
    ancestor = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", freeze, commit])
    require(ancestor.returncode == 0, f"Freeze commit {freeze} is not an ancestor of {commit}")
    freeze_time = git(repo, "show", "-s", "--format=%cI", freeze).strip()

    require(not any(m in sys.modules for m in MODULES), "Analysis modules already imported")
    sys.path.insert(0, str(snap))
    try:
        analysis, h, prov = (importlib.import_module(m) for m in ("analyze", "harness", "provenance"))
        checks = reconcile(contract, exp, manifest_blob, log_blob, protocol, raw_path, analysis, h, prov)
    finally:
        sys.path.remove(str(snap))
        for m in MODULES:
            sys.modules.pop(m, None)

    reports = {}
    collection_report = run_analyzer(coll, raw_path, out / "analysis_collection.md")
    snapshot_report = run_analyzer(snap, raw_path, out / "analysis_snapshot.md")
    for name, blob in (("analysis_collection.md", collection_report), ("analysis_snapshot.md", snapshot_report)):
        require(sha(blob) == contract["expected_reports"][name], f"Report differs from pinned output: {name}")
        reports[name] = sha(blob)
    require(collection_report == committed, "Collection analyzer does not reproduce the committed analysis")
    reports["committed_analysis_byte_identical_to"] = "analysis_collection.md"
    reports["snapshot_vs_committed"] = compare_reports(committed.decode(), snapshot_report.decode())

    canonical = commit == contract["source_snapshot"] and not tracked_changes
    summary = {
        "status": "provenance_replay_passed" if canonical
                  else "provenance_replay_passed_noncanonical_checkout",
        "artifact_snapshot": contract["source_snapshot"],
        "analysis_checkout_commit": commit, "tracked_checkout_dirty": bool(tracked_changes),
        "freeze_commit": freeze, "freeze_commit_committer_time": freeze_time,
        "collection_sources_commit": source["commit"],
        "python": platform.python_version(), "platform": platform.platform(),
        "input_contract_sha256": sha(contract_path.read_bytes()),
        "replay_script_sha256": sha(pathlib.Path(__file__).resolve().read_bytes()),
        **checks, "reports": reports, "notes": contract["notes"],
        "limits": ["No fresh inference; hosted models can drift",
                   "Logged turns are logical calls; transport retries inside a call, and their cost and "
                   "served model, were not recorded by the collection harness",
                   "The one failed worker turn has no served-model ID",
                   "Manifest cost is the CLI-reported figure; it is recorded, not verified",
                   "Git committer times are self-reported, not third-party timestamps",
                   "One model, one fixed pipeline, one synthetic task; two fixed objective strings per wording",
                   "Report hashes checked on CPython 3.11 and 3.12",
                   "v2 and SAE studies are outside this replay"]}
    (out / "audit.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    outputs = sorted(out.iterdir())
    (out / "SHA256SUMS").write_text("".join(f"{sha(p.read_bytes())}  {p.name}\n" for p in outputs))
    return summary


def reconcile(contract, exp, manifest_blob, log_blob, protocol, raw_path, analysis, h, prov):
    manifest = json.loads(manifest_blob)
    totals = manifest["totals"]
    argv = manifest["argv"]
    lo, hi = contract["seed_range"]
    seeds = list(range(lo, hi + 1))
    require(manifest["status"] == "complete", "Manifest status is not complete")
    for key in ("run_id", "study", "phase", "backend", "model", "freeze_commit"):
        require(manifest[key] == contract[key], f"Manifest {key} differs from contract")
    require(manifest["git"] == {"commit": contract["freeze_commit"], "dirty": False},
            "Manifest collection commit is not the clean freeze commit")
    require(manifest["protocol_hash"] == sha(protocol), "Manifest protocol_hash differs from protocol file")
    require((argv["seed_offset"], argv["seeds"], argv["workers"], argv["schedule_seed"])
            == (lo, len(seeds), 4, 20261107) and sorted(argv["wordings"].split(",")) == contract["wordings"],
            "Manifest arguments differ from the held-out protocol")
    require(manifest["resolved_model"] == contract["served_model"], "Manifest resolved_model differs")
    require(manifest["prompt_hash"] == h.prompt_hash(prov.TEMPLATES) and manifest["prompts"] == prov.TEMPLATES,
            "Manifest prompts do not match provenance.py templates")
    require((totals["rows"], totals["failed_rows"], totals["calls"], totals["errors"])
            == (exp["rows"], exp["manifest_failed_rows"], exp["manifest_calls"], exp["manifest_errors"]),
            f"Manifest totals differ from contract: {totals}")
    require(log_blob.decode().splitlines()[0] == f"{prov.STUDY}: {totals['rows']} rows, "
            f"{totals['calls']} calls, {totals['failed_rows']} failed rows", "Run log differs from manifest totals")

    rows = [json.loads(line) for line in raw_path.read_text().splitlines() if line.strip()]
    require(len(rows) == exp["rows"], "Row count mismatch")
    require(list(prov.CONDITIONS) == contract["conditions"] and list(prov.OBJECTIVES) == contract["authorizations"]
            and sorted(prov.WORDINGS) == contract["wordings"], "Design factors differ from provenance.py")
    for r in rows:
        require(all(r[k] == manifest[k] for k in RUN_METADATA), f"Run metadata mismatch at seed {r['seed']}")
        require(r["study"] == r["design"] == prov.STUDY, "Study label mismatch")
    keys = [(r["cond"], r["authorization"], r["framing"], r["seed"]) for r in rows]
    require(len(set(keys)) == len(keys), "Duplicate trial keys")
    cells = {}
    for r in rows:
        cells.setdefault(f"{r['cond']}|{r['authorization']}|{r['framing']}", []).append(r)
    require(len(cells) == exp["cells"] == len(contract["conditions"]) * len(contract["authorizations"])
            * len(contract["wordings"]), "Cell count mismatch")
    require(all(sorted(r["seed"] for r in rs) == seeds and len(rs) == exp["seeds_per_cell"]
                for rs in cells.values()), "Each cell must hold every held-out seed exactly once")

    # Turn-level accounting: served model, failures, call counter, monitor verdicts, protocol replies.
    turns = [(r, t) for r in rows for t in r["turns"]]
    failed = [(r, t) for r, t in turns if t["failed"]]
    require(len(turns) == exp["logged_turns"], f"Logged turns {len(turns)} != {exp['logged_turns']}")
    require(len(failed) == exp["failed_turns"] == totals["errors"], "Failed-turn count mismatch")
    require(len(turns) == totals["calls"] + totals["errors"],
            "Logged turns do not equal manifest calls + errors (see notes.call_counter)")
    require(all(t["model"] == contract["served_model"] for _, t in turns if not t["failed"]),
            "A successful turn lacks the expected served model")
    require(all(t["model"] is None for _, t in failed), "Failed turn unexpectedly records a model")
    failed_rows = [{"cond": r["cond"], "authorization": r["authorization"], "framing": r["framing"],
                    "seed": r["seed"], "failed_calls": r["failed_calls"],
                    "failed_role": t["role"], "failed_agent": t["agent"]} for r, t in failed]
    require(failed_rows == exp["failed_trials"]
            and sum(r["failed_calls"] > 0 for r in rows) == len(exp["failed_trials"]),
            f"Failed trials differ from contract: {failed_rows}")
    monitor = [(r, t) for r, t in turns if t["role"] == "monitor"]
    malformed = sum(t["raw"].strip() not in ("ALLOW", "BLOCK") and not t["failed"] for _, t in monitor)
    blocks = sum(t["decision"] == "BLOCK" for _, t in monitor)
    allows_auth = sum(t["decision"] == "ALLOW" and r["authorization"] == "authorized" for r, t in monitor)
    require(malformed == exp["malformed_monitor_verdicts"] == sum(r["protocol_errors"] for r in rows),
            "Malformed monitor verdict count mismatch")
    require((len(monitor), blocks, allows_auth, len(monitor) - blocks)
            == (exp["monitor_proposals"], exp["monitor_blocks"], exp["monitor_allows_authorized"],
                exp["monitor_allows_authorized"]), "Monitor verdict counts differ from contract")
    nonprotocol = sum(t["role"] != "monitor" and not t["failed"] and t["proposed"] is None
                      and (t["raw"] or "").strip().upper() != "PASS" for _, t in turns)
    require(nonprotocol == exp["nonprotocol_replies"] == sum(r["nonprotocol_replies"] for r in rows),
            "Non-protocol reply count mismatch")

    # Re-execute each trial's protocol logic from its logged replies, then rescore stored rows directly.
    class ReplayBackend(h.Backend):
        def __init__(self, logged):
            self._init_counters()
            self.queue = list(logged)

        def __call__(self, system, user):
            t = self.queue.pop(0)
            if t["failed"]:
                return self._fail("replayed")
            self.calls += 1
            self.tl.model = t["model"]
            return t["raw"]

    def strip_turns(row, extra=()):
        return [{k: v for k, v in t.items() if k not in ("ms", *extra)} for t in row["turns"]]

    score_fields = None
    for r in rows:
        backend = ReplayBackend(r["turns"])
        rebuilt = prov.run_trial(backend, r["seed"], r["cond"], r["authorization"], r["framing"])
        require(not backend.queue, f"Unconsumed logged turns at {r['cond']} seed {r['seed']}")
        stored = {k: v for k, v in r.items() if k not in RUN_METADATA}
        require(set(rebuilt) == set(stored)
                and all(rebuilt[k] == stored[k] for k in stored if k != "turns")
                and strip_turns(rebuilt, ("fail_reason",)) == strip_turns(r),
                f"Rebuilt trial differs from stored row: {r['cond']}/{r['authorization']}/"
                f"{r['framing']} seed {r['seed']}")
        rescored = prov.score_row(r)
        score_fields = sorted(rescored)
        require(all(rescored[k] == r[k] for k in rescored), f"Stored score differs at seed {r['seed']}")
        require(r["board"] == [f"[{t['agent']}] {t['posted']}" for t in r["turns"] if t.get("posted")],
                f"Board is not the accepted posts at seed {r['seed']}")

    tallies, bounds = {}, {}
    for key, rs in sorted(cells.items()):
        valid = [r for r in rs if r["failed_calls"] == 0]
        tallies[key] = [len(valid), sum(r["recoverable"] for r in valid), sum(r["assembled"] for r in valid)]
        if len(valid) < len(rs):
            n, miss = len(rs), len(rs) - len(valid)
            bounds[key] = {m: [tallies[key][i] / n, (tallies[key][i] + miss) / n]
                           for i, m in ((1, "recoverable"), (2, "assembled"))}
    require(tallies == exp["cells_valid_recoverable_assembled"], "Cell tallies differ from contract")

    enriched = [analysis.enrich(r) for r in rows]
    contrasts = analysis.paired_contrasts(enriched, "local")
    ia, iw = analysis.IDENTITY.index("authorization"), analysis.IDENTITY.index("framing")
    found = []
    for e in exp["provenance_vs_local"]:
        p, = [p for p in contrasts if p["cond"] == "provenance"
              and (p["group"][ia], p["group"][iw]) == (e["authorization"], e["framing"])]
        mean, ci = p[e["metric"]]
        b, c, pval = p[e["metric"] + "_disc"]
        got = {"pairs": p["n_pairs"], "diff_pp": int(f"{mean * 100:.0f}"),
               "ci_pp": [int(f"{x * 100:.0f}") for x in ci], "discordant_plus": b, "discordant_minus": c}
        require(all(got[k] == e[k] for k in got), f"Contrast {e['label']} differs: {got}")
        found.append({**e, "mcnemar_p": pval})

    return {"rows": len(rows), "cells": len(cells), "logged_turns": len(turns),
            "failed_turns": len(failed), "manifest_totals": totals,
            "call_counter_identity": "logged_turns == manifest calls + errors",
            "failed_trials": failed_rows, "failed_cell_all_trial_bounds": bounds,
            "served_model_on_successful_turns": contract["served_model"],
            "monitor": {"proposals": len(monitor), "block": blocks, "allow": len(monitor) - blocks,
                        "allow_in_authorized_trials": allows_auth, "malformed": malformed},
            "nonprotocol_replies": nonprotocol, "trials_rebuilt_from_logged_replies": len(rows),
            "stored_scores_reproduced": len(rows), "score_fields": score_fields,
            "cells_valid_recoverable_assembled": tallies, "provenance_vs_local": found,
            "manifest_reported_cost_usd": totals.get("cost"),
            "manifest_prompt_hash_reproduced": True, "protocol_sha256": sha(protocol)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path,
                        default=pathlib.Path(__file__).resolve().parents[3])
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args(argv)
    repo, out = args.repo.resolve(), args.out.resolve()
    require(not out.exists(), f"Refusing to overwrite output: {out}")
    require(not out.is_relative_to(repo), "Output must be outside the source checkout")
    contract_path = CONTRACT_PATH
    contract = json.loads(contract_path.read_text())
    out.parent.mkdir(parents=True, exist_ok=True)
    # Build the packet beside its destination and rename it only after every check
    # passes, so a failed run leaves no partial output behind.
    tmp = pathlib.Path(tempfile.mkdtemp(prefix=f".{out.name}.partial-", dir=out.parent))
    try:
        with tempfile.TemporaryDirectory() as work:
            summary = replay(repo, contract, contract_path, tmp, pathlib.Path(work))
        os.rename(tmp, out)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    m = summary["monitor"]
    print(f"PASS: {summary['rows']} trials in {summary['cells']} cells; {summary['logged_turns']} logged turns "
          f"= {summary['manifest_totals']['calls']} manifest calls + {summary['failed_turns']} failed; "
          f"{summary['trials_rebuilt_from_logged_replies']} trials rebuilt and rescored; "
          f"{m['malformed']} malformed verdicts; {summary['nonprotocol_replies']} non-protocol replies; "
          f"committed analysis reproduced byte-identically. Outputs: {out}")
    if summary["status"] != "provenance_replay_passed":
        print(f"NOTE: checkout is not a clean copy of {contract['source_snapshot']}; "
              "audit status is provenance_replay_passed_noncanonical_checkout.")


def cli():
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
