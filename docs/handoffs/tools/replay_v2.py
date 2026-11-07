#!/usr/bin/env python3
"""Replay the pinned v2 artifact snapshot offline without altering source data.

This verifies historical artifacts, not fresh hosted-model inference or the
unmerged provenance study. Only Python's standard library is required.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def replay(repo, contract, contract_path, tmp, src):
    for item in contract["files"]:
        path = repo / item["path"]
        require(path.is_file(), f"Missing input: {item['path']}")
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"],
                f"SHA256 mismatch: {item['path']}")
        if item.get("kind") == "analysis_source":
            # Run analysis from a copy of the verified bytes only, so untracked
            # files next to the originals cannot shadow imports.
            (src / path.name).write_bytes(data)

    # Import only after checking all source and result hashes. No backend is instantiated.
    sys.path.insert(0, str(src))
    spec = importlib.util.spec_from_file_location("v2_audit_analysis", src / "analyze.py")
    analysis = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analysis)
    runs, all_rows, groups = [], [], {}
    for item in contract["files"]:
        if item.get("kind") != "raw":
            continue
        path = repo / item["path"]
        rows = analysis.load_rows([str(path)])
        manifest = json.loads(pathlib.Path(str(path) + ".manifest.json").read_text())
        calls = sum(len(row["turns"]) for row in rows)
        require(manifest["status"] == "complete", f"Incomplete manifest: {path.name}")
        require(len(rows) == item["rows"] == manifest["totals"]["rows"],
                f"Row denominator mismatch: {path.name}")
        require(not any(analysis.is_preschema(row) for row in rows),
                f"Pre-schema rows present: {path.name}")
        require(calls == item["logical_calls"] == manifest["totals"]["calls"],
                f"Logical-call denominator mismatch: {path.name}")
        require(all(row["run_id"] == manifest["run_id"] for row in rows),
                f"Run identity mismatch: {path.name}")
        require(all(row.get("failed_calls") == 0 for row in rows)
                and manifest["totals"]["failed"] == 0,
                f"Failure status differs from audited snapshot: {path.name}")
        keys = [(r["cond"], r["seed"], r.get("n"), r.get("k")) for r in rows]
        require(len(keys) == len(set(keys)), f"Duplicate trial keys: {path.name}")
        enriched = [analysis.enrich(row) for row in rows]
        check = analysis.legacy_check(enriched)
        require(check["n_stored"] == len(rows) == check["n_reproduced"]
                and not check["mismatch"], f"Stored-score mismatch: {path.name}")
        all_rows.extend(rows)
        groups.setdefault(item["group"], []).append(item["path"])
        runs.append({"path": item["path"], "run_id": manifest["run_id"],
                     "rows": len(rows), "distinct_seeds": len({r["seed"] for r in rows}),
                     "logical_calls": calls, "legacy_reproduced": check["n_reproduced"],
                     "collection_git": manifest["git"],
                     "reported_served_models": manifest["resolved_model"],
                     "reported_totals": manifest["totals"]})
    require(len(all_rows) == contract["expected_rows"], "Total row mismatch")
    require(sum(r["logical_calls"] for r in runs) == contract["expected_logical_calls"],
            "Total logical-call mismatch")
    commit = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    tracked_changes = subprocess.check_output(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=no"], text=True)
    for group, paths in sorted(groups.items()):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            analysis.main([*[str(repo / p) for p in paths], "--legacy-check"])
        require(not stderr.getvalue().strip(), f"Unexpected analyzer warning: {stderr.getvalue()}")
        report = tmp / (group + ".md")
        report.write_text(stdout.getvalue())
        require(digest(report) == contract["expected_reports"][report.name],
                f"Report differs from pinned output: {report.name}")
    canonical = commit == contract["source_snapshot"] and not tracked_changes
    summary = {
        "status": "artifact_replay_passed" if canonical
                  else "artifact_replay_passed_noncanonical_checkout",
        "artifact_snapshot": contract["source_snapshot"],
        "analysis_checkout_commit": commit, "tracked_checkout_dirty": bool(tracked_changes),
        "python": platform.python_version(), "platform": platform.platform(),
        "input_contract_sha256": digest(contract_path),
        "replay_script_sha256": digest(pathlib.Path(__file__).resolve()),
        "rows": len(all_rows), "logical_calls": sum(r["logical_calls"] for r in runs),
        "legacy_reproduced": sum(r["legacy_reproduced"] for r in runs), "runs": runs,
        "limits": ["No fresh inference; hosted models can drift",
                   "Logical calls are not a reconstruction of every transport retry",
                   "Original Sonnet strict/explicit run has mixed served-model IDs",
                   "Sonnet rerun reuses tasks and is analyzed separately",
                   "Group reports must match pinned hashes (checked on CPython 3.11-3.13)",
                   "Provenance and SAE studies are outside this replay"]}
    (tmp / "audit.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    outputs = sorted(tmp.iterdir())
    (tmp / "SHA256SUMS").write_text("".join(f"{digest(p)}  {p.name}\n" for p in outputs))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path,
                        default=pathlib.Path(__file__).resolve().parents[3])
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    require(not out.exists(), f"Refusing to overwrite output: {out}")
    require(not out.is_relative_to(repo), "Output must be outside the source checkout")
    contract_path = pathlib.Path(__file__).resolve().parents[1] / "v2-inputs.json"
    contract = json.loads(contract_path.read_text())
    out.parent.mkdir(parents=True, exist_ok=True)
    # Build the packet beside its destination and rename it only after every check
    # passes, so a failed run leaves no partial output behind.
    tmp = pathlib.Path(tempfile.mkdtemp(prefix=f".{out.name}.partial-", dir=out.parent))
    try:
        with tempfile.TemporaryDirectory() as src:
            summary = replay(repo, contract, contract_path, tmp, pathlib.Path(src))
        os.rename(tmp, out)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    print(f"PASS: {summary['rows']} rows; {summary['logical_calls']} logical calls; "
          f"{summary['legacy_reproduced']} stored legacy scores reproduced. Outputs: {out}")
    if summary["status"] != "artifact_replay_passed":
        print(f"NOTE: checkout is not a clean copy of {contract['source_snapshot']}; "
              "audit status is artifact_replay_passed_noncanonical_checkout.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
