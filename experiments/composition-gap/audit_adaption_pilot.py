"""Portable, read-only audit of the published Adaption pilot; no model service.

Historical absolute paths are provenance, not paths to open on this machine.
Resolve only the three published sibling directories and verify their hashes.
This checks saved evidence; it neither resumes collection nor changes approval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import adaption_pilot as pilot
import adaption_resume as resume
import analyze
from scoring import score_row

PUBLISHED_ARTIFACTS = {"amendments.jsonl", "analysis.md", "calls.jsonl", "combined_trials.jsonl",
                       "completed_trials.jsonl", "manifest.json",
                       "manifest.before-amendment-736ad7fd2fb24855a566d2991969747d.json"}
SOURCE_PROTOCOL = resume.p.PROTOCOL.relative_to(pilot.ROOT).as_posix()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_number(actual, expected, label):
    require(math.isclose(actual, expected, rel_tol=0, abs_tol=1e-10), label + " differs")


def audit(results_root=pilot.RESULTS):
    root = Path(results_root).resolve()
    directory = root / "pilot-03-resume"
    manifest = json.loads((directory / "manifest.json").read_text())
    summary = json.loads((directory / "summary.json").read_text())
    require(manifest["status"] == "complete", "collection has not finished")
    plan, totals = manifest["plan"], manifest["totals"]
    config = plan["config"]
    source = root / "pilot-02"
    require(Path(plan["source"]).name == source.name, "unexpected historical source")
    require([Path(x).name for x in plan["histories"]] == ["pilot-01"], "unexpected cost history")
    require({Path(x["path"]).name for x in plan["input_hashes"]} == {"pilot-01", "pilot-02"},
            "unexpected historical input hash set")
    for item in plan["input_hashes"]:
        local = root / Path(item["path"]).name
        require(set(item["files"]) == {"manifest.json", "trials.jsonl", "calls.jsonl"},
                "historical input hashes are incomplete")
        for name, expected in item["files"].items():
            require(resume.file_hash(local / name) == expected, "historical input hash differs: " + name)
    require(set(summary["artifact_sha256"]) == PUBLISHED_ARTIFACTS, "published artifact hash set differs")
    for name, expected in summary["artifact_sha256"].items():
        require(Path(name).name == name, "artifact hash must name a sibling file")
        require(resume.file_hash(directory / name) == expected, "published artifact hash differs: " + name)

    rows = resume.read_jsonl(directory / "combined_trials.jsonl")
    expected = {(m["id"], s, c, a) for m, s, c, a in pilot.jobs(config)}
    require(len(rows) == len(expected) == 24 and {resume.trial_key(r) for r in rows} == expected,
            "expected 24 unique assigned trial keys")
    analyze.validate_rows(rows, analyze.DEFAULT_BY)
    require({r["run_id"] for r in rows} == {manifest["run_id"]} and
            {r["protocol_hash"] for r in rows} == {manifest["protocol_hash"]}, "analysis identity differs")
    _, originals, source_events = resume.validate_source(source, config, current_files=False)
    preserved = [r for r in originals if r["failed_calls"] == 0]
    for original in preserved:
        derived = next(r for r in rows if resume.trial_key(r) == resume.trial_key(original))
        for field, value in (("source_row_sha256", pilot.digest(original)),
                             ("source_run_id", original["run_id"]),
                             ("source_protocol_hash", original["protocol_hash"]),
                             ("turns", original["turns"]), ("board", original["board"])):
            require(derived[field] == value, "retained source trial differs: " + field)
    events = resume.read_jsonl(directory / "calls.jsonl")
    current_results = resume.validate_current(events, manifest, expected, config)
    _, source_results, _, _ = resume.journal_attempts(source_events, config)
    for row in rows:
        require(row["study"] == row["design"] == pilot.STUDY, "study identity differs")
        score = score_row(row)
        require(all(row[k] == score[k] for k in ("assembled", "recoverable", "valid")), "stored score differs")
        resume.validate_trial(row, config, {**source_results, **current_results})
    source_successes = {(resume.trial_key(r), i) for r in originals
                        for i, turn in enumerate(r["turns"]) if not turn["failed"]}
    successes = set(source_successes)
    for event in events:
        logical = (tuple(event["trial_key"]), event["turn_index"])
        if event["event"] == "attempt":
            require(logical not in successes, "a recorded successful turn was resent")
        elif event["record"]["failure"] is None:
            successes.add(logical)
    _, attempts_by_turn = resume.collect_cache(originals, source_events, events)
    maximum_attempts = max(map(len, attempts_by_turn.values()))
    require(maximum_attempts <= plan["max_attempts_per_turn"], "logical retry allowance exceeded")

    segments = []
    call_ids = set()
    input_tokens = output_tokens = reasoning_tokens = usage_responses = 0
    models = {m["id"]: {"post_attempts": 0, "usage_bearing_responses": 0, "input_tokens": 0,
                        "output_tokens": 0, "reasoning_tokens": 0, "known_estimated_credits": 0.0,
                        "uncertain_reserved_credits": 0.0} for m in config["models"]}
    def committed_hash(commit, path):
        blob = subprocess.run(["git", "show", commit + ":" + path],
                              cwd=pilot.ROOT, capture_output=True, check=True).stdout
        return hashlib.sha256(blob).hexdigest()
    source_plan = json.loads((source / "manifest.json").read_text())
    require(committed_hash(source_plan["git"]["commit"], SOURCE_PROTOCOL)
            == source_plan["plan"]["source_protocol_sha256"],
            "collection commit does not match recorded source protocol hash")
    for segment in (root / "pilot-01", source, directory):
        segment_manifest = json.loads((segment / "manifest.json").read_text())
        segment_plan = segment_manifest["plan"]
        # Preserve collection commits in history: current code can include later safety fixes.
        recorded_hashes = segment_plan.get("implementation_sha256", segment_plan.get("source_files_sha256"))
        expected_sources = set(pilot.SOURCE_FILES) | ({"adaption_resume.py"} if segment == directory else set())
        require(set(recorded_hashes) == expected_sources, "collection source hash set differs")
        for name, expected_hash in recorded_hashes.items():
            require(Path(name).name == name, "unexpected recorded source filename")
            require(committed_hash(segment_manifest["git"]["commit"], "experiments/composition-gap/" + name)
                    == expected_hash,
                    "collection commit does not match recorded source hash: " + name)
        attempts, results, known, uncertain = resume.journal_attempts(
            resume.read_jsonl(segment / "calls.jsonl"), segment_plan["config"])
        require(not call_ids.intersection(attempts), "physical call ID reused across segments")
        call_ids.update(attempts)
        for call_id in attempts:
            model = models[attempts[call_id]["request"]["model"]]
            model["post_attempts"] += 1
            record = results.get(call_id, {}).get("record")
            if record and record.get("estimated_credits") is not None:
                usage = record["usage"]
                usage_responses += 1
                input_tokens += usage["input_tokens"]
                output_tokens += usage["output_tokens"]
                reasoning_tokens += (usage.get("output_tokens_details") or {}).get("reasoning_tokens", 0) or 0
                model["usage_bearing_responses"] += 1
                model["input_tokens"] += usage["input_tokens"]
                model["output_tokens"] += usage["output_tokens"]
                model["reasoning_tokens"] += (usage.get("output_tokens_details") or {}).get("reasoning_tokens", 0) or 0
                model["known_estimated_credits"] += record["estimated_credits"]
            else:
                model["uncertain_reserved_credits"] += resume.reservation(attempts[call_id]["request"], segment_plan["config"])
        segments.append({"directory": segment.name, "post_attempts": len(attempts),
                         "known_estimated_credits": known, "uncertain_reserved_credits": uncertain})
    known = math.fsum(x["known_estimated_credits"] for x in segments)
    uncertain = math.fsum(x["uncertain_reserved_credits"] for x in segments)
    same_number(known, totals["total_known_credits"], "manifest known estimate")
    same_number(uncertain, totals["total_reserved_credits"], "manifest reservation")
    require(known + uncertain <= config["max_credits"], "estimated allowance exceeded")
    require(set(summary["models"]) == set(models), "published model set differs")
    for name, values in models.items():
        for key, value in values.items():
            same_number(value, summary["models"][name][key], "published model " + name + " " + key)
    cells = []
    for name in models:
        for auth in config["authorizations"]:
            for cond in config["conditions"]:
                selected = [r for r in rows if (r["model"], r["authorization"], r["cond"]) == (name, auth, cond)]
                valid = [r for r in selected if r["valid"]]
                cells.append({"model": name, "authorization": auth, "condition": cond,
                              "assigned": len(selected), "valid": len(valid), "failed": len(selected) - len(valid),
                              "assembled": sum(r["assembled"] for r in valid),
                              "recoverable": sum(r["recoverable"] for r in valid),
                              "nonprotocol_replies": sum(r["nonprotocol_replies"] for r in selected)})
    require(cells == summary["cells"], "published cell counts differ")
    result = {"run_id": manifest["run_id"], "status": "offline_audit_passed",
              "assigned_trials": len(rows), "unique_trial_keys": len(expected),
              "valid_trials": sum(r["valid"] for r in rows),
              "failed_trials": sum(not r["valid"] for r in rows),
              "preserved_source_trials": len(preserved),
              "successful_source_calls_not_resent": len(source_successes),
              "maximum_attempts_per_logical_turn": maximum_attempts,
              "cumulative_actual_post_attempts": len(call_ids),
              "cumulative_known_estimated_credits": known,
              "cumulative_uncertain_reserved_credits": uncertain,
              "cumulative_accounted_credits": known + uncertain,
              "estimated_limit": config["max_credits"], "usage_bearing_responses": usage_responses,
              "input_tokens": input_tokens, "output_tokens": output_tokens, "reasoning_tokens": reasoning_tokens,
              "segments": segments, "models": models, "cells": cells,
              "billing_caveat": "Configured-rate estimates; the original 504 usage and final invoice remain unverified."}
    for key in ("assigned_trials", "unique_trial_keys", "valid_trials", "failed_trials", "preserved_source_trials",
                "successful_source_calls_not_resent", "maximum_attempts_per_logical_turn",
                "cumulative_actual_post_attempts", "cumulative_known_estimated_credits",
                "cumulative_uncertain_reserved_credits", "cumulative_accounted_credits", "estimated_limit"):
        same_number(result[key], summary[key], "published summary " + key)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, default=pilot.RESULTS)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(audit(args.results_root), indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
