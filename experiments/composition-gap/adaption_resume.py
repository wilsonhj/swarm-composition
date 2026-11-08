"""Bounded, journaled continuation of an Adaption pilot; default is offline planning.

Historical files are read-only. Successful calls are replayed exactly, transient
failures can be retried at most three total sends per logical turn, and every
ambiguous attempt keeps its own credit reservation. No exactly-once provider
execution is claimed. The combined dataset has explicit derived-run lineage.
"""
import argparse
import copy
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import uuid

import adaption_backend as api
import adaption_pilot as pilot
import analyze
import harness as h
import provenance as p
from scoring import score_row

MAX_ATTEMPTS = 3
BACKOFF = (5, 15)
TRANSIENT_HTTP = (502, 503, 504)
TERMINAL_GENERATION = ("status_not_completed", "incomplete", "empty_output")
DEFAULT_SOURCE = pilot.RESULTS / "pilot-02"
DEFAULT_HISTORY = pilot.RESULTS / "pilot-01"
CLAIMS = ".resume-claims.jsonl"  # one {source_run_id, output} line per started continuation


def trial_key(row):
    return (row["model"], row["seed"], row["cond"], row["authorization"])


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_directory(path):
    descriptor = os.open(str(path), os.O_RDONLY)
    try: os.fsync(descriptor)
    finally: os.close(descriptor)


def read_jsonl(path, recover=False):
    if not path.exists():
        return []
    data = path.read_bytes()
    rows, offset = [], 0
    lines = data.splitlines(keepends=True)
    for index, line in enumerate(lines):
        try:
            value = json.loads(line)
        except (ValueError, UnicodeError):
            if not recover or index != len(lines) - 1 or line.endswith(b"\n"):
                raise ValueError(f"malformed journal: {path.name}") from None
            # Preserve the incomplete tail before repairing this mutable journal.
            tail = path.with_name(path.name + ".interrupted-" + uuid.uuid4().hex)
            with tail.open("xb") as stream:
                stream.write(line); stream.flush(); os.fsync(stream.fileno())
            sync_directory(path.parent)
            with path.open("r+b") as stream:
                stream.truncate(offset); stream.flush(); os.fsync(stream.fileno())
            break
        if not isinstance(value, dict):
            raise ValueError(f"journal row must be an object: {path.name}")
        rows.append(value)
        offset += len(line)
    if recover and data and lines[-1] and not lines[-1].endswith(b"\n") and offset == len(data):
        with path.open("ab") as stream:
            stream.write(b"\n"); stream.flush(); os.fsync(stream.fileno())
    if recover:
        sync_directory(path.parent)
    return rows


def append(path, value):
    with path.open("a") as stream:
        stream.write(json.dumps(value, allow_nan=False) + "\n")
        stream.flush(); os.fsync(stream.fileno())
    sync_directory(path.parent)


def atomic_jsonl(path, rows):
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w") as stream:
        for row in rows:
            stream.write(json.dumps(row, allow_nan=False) + "\n")
        stream.flush(); os.fsync(stream.fileno())
    tmp.replace(path)
    sync_directory(path.parent)


def write_manifest(path, value):
    atomic_jsonl(path, [value])


def request_for(model, system, user, config):
    return {"model": model, "instructions": system, "input": user,
            "max_output_tokens": config["max_output_tokens"], "temperature": 0,
            "tools": [], "tool_choice": "none", "agentic_memory": False,
            "store": False, "stream": False, "background": False}


def reservation(request, config):
    model = next(m for m in config["models"] if m["id"] == request["model"])
    return (config["input_token_budget"] * model["input_credits_per_million"] +
            request["max_output_tokens"] * model["output_credits_per_million"]) / 1_000_000


def journal_attempts(events, config):
    attempts, results = {}, {}
    for event in events:
        call_id = event["call_id"]
        if event["event"] == "attempt":
            if call_id in attempts:
                raise ValueError("duplicate attempt ID")
            attempts[call_id] = event
        elif event["event"] == "result":
            if call_id in results:
                raise ValueError("duplicate result ID")
            results[call_id] = event
        else:
            raise ValueError("unknown call journal event")
    for call_id, event in results.items():
        if event["record"].get("call_id") != call_id:
            raise ValueError("result call ID differs from its record")
        if event["record"]["sent"] and call_id not in attempts:
            raise ValueError("sent result has no durable attempt")
        if call_id in attempts:
            attempt = attempts[call_id]
            if attempt["request"] != event["record"]["request"]:
                raise ValueError("attempt/result request differs")
            for field in ("run_id", "trial_key", "turn_index", "requested_model", "seed", "cond", "authorization"):
                if attempt.get(field) != event.get(field):
                    raise ValueError("attempt/result context differs")
    known, uncertain = 0.0, 0.0
    for call_id, event in attempts.items():
        result = results.get(call_id)
        record = result["record"] if result else None
        cost = record.get("estimated_credits") if record else None
        if cost is not None:
            if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
                raise ValueError("invalid journal cost")
            usage = record.get("usage") or {}
            if any(type(usage.get(k)) is not int or usage[k] < 0 for k in ("input_tokens", "output_tokens")):
                raise ValueError("known cost has invalid usage")
            model = next(m for m in config["models"] if m["id"] == event["request"]["model"])
            recomputed = (usage["input_tokens"] * model["input_credits_per_million"] +
                          usage["output_tokens"] * model["output_credits_per_million"]) / 1_000_000
            if not math.isclose(cost, recomputed, abs_tol=1e-12):
                raise ValueError("journal cost differs from usage")
            known += cost
        else:
            uncertain += reservation(event["request"], config)
    return attempts, results, known, uncertain


def load_source(source):
    manifest = json.loads((source / "manifest.json").read_text())
    rows = read_jsonl(source / "trials.jsonl")
    events = read_jsonl(source / "calls.jsonl")
    if manifest["status"] == "running" or manifest["mock_only"] or manifest["study"] != pilot.STUDY:
        raise ValueError("source must be a stopped/completed real pilot")
    analyze.validate_rows(rows, analyze.DEFAULT_BY)
    return manifest, rows, events


def validate_source(source, config, current_files=True):
    """current_files=False is for the offline audit, which checks these hashes
    against the source's collection commit instead of the working tree."""
    manifest, rows, events = load_source(source)
    if manifest["plan"]["config"] != config:
        raise ValueError("source experiment configuration differs")
    if manifest["prompt_hash"] != h.prompt_hash(p.TEMPLATES):
        raise ValueError("source prompts differ")
    if current_files and manifest["plan"]["source_protocol_sha256"] != file_hash(p.PROTOCOL):
        raise ValueError("source frozen protocol differs")
    for name in ("harness.py", "provenance.py", "scoring.py"):
        if current_files and manifest["plan"]["source_files_sha256"][name] != file_hash(pilot.HERE / name):
            raise ValueError("source task/scoring implementation differs")
    expected = {(m["id"], s, c, a) for m, s, c, a in pilot.jobs(config)}
    _, result_events, _, _ = journal_attempts(events, config)
    seen = set()
    for row in rows:
        key = trial_key(row)
        if key not in expected or key in seen or row["run_id"] != manifest["run_id"]:
            raise ValueError("unexpected or duplicate source trial")
        if row["study"] != pilot.STUDY or row["protocol_hash"] != manifest["protocol_hash"]:
            raise ValueError("source trial identity differs")
        if row["framing"] != config["wording"] or row["prompt_hash"] != manifest["prompt_hash"]:
            raise ValueError("source trial prompts differ")
        score = score_row(row)
        if any(row[k] != score[k] for k in ("assembled", "recoverable")):
            raise ValueError("source stored score differs")
        seen.add(key)
        validate_trial(row, config, result_events, final=False)
    # The original runner writes a trial only after all its calls. An aborted
    # run can therefore have durable attempts or results with no saved row.
    # Their logical turn cannot safely be reconstructed from the row data.
    row_call_ids = {turn["adaption"]["call_id"] for row in rows for turn in row["turns"]}
    if any(event["call_id"] not in row_call_ids for event in events):
        raise ValueError("source journal contains calls without a saved trial")
    return manifest, rows, events


def validate_trial(row, config, result_events, final=True):
    """Reconstruct the exact prompt sequence and scores using only saved replies."""
    turns = row["turns"]
    if len(turns) != 5:
        raise ValueError("trial must contain five actor turns")
    class Replay(h.Backend):
        def __init__(self): self._init_counters(cost=None); self.index = 0
        def __call__(self, system, user):
            turn = turns[self.index]; self.index += 1
            record = turn["adaption"]
            if record["request"] != request_for(row["model"], system, user, config):
                raise ValueError("trial prompt differs from saved request")
            saved = result_events.get(record["call_id"])
            if saved is None or saved["record"] != record:
                raise ValueError("trial record is not linked to the call journal")
            self.tl.model = turn.get("model")
            if turn["failed"]:
                failure = record["failure"]
                if (failure is None or turn["fail_reason"] != failure or
                        (final and failure not in TERMINAL_GENERATION + ("trial_stopped",)) or turn["raw"] != "PASS"):
                    raise ValueError("failed turn lacks a matching terminal failure record")
                self._fail(failure)
            elif record["failure"] is not None or record["model"] != row["model"]:
                raise ValueError("successful trial turn contains a backend failure")
            elif record_text(record) != turn["raw"]:
                raise ValueError("saved reply differs from provider response text")
            return turn["raw"]
    replay = Replay()
    rebuilt = p.run_trial(replay, row["seed"], row["cond"], row["authorization"], row["framing"])
    for field in ("board", "assembled", "recoverable", "failed_calls", "nonprotocol_replies", "actor_calls"):
        if rebuilt[field] != row[field]:
            raise ValueError("trial content differs from replay: " + field)


def validate_current(events, manifest, expected, config):
    attempts, results, _, _ = journal_attempts(events, config)
    for event in events:
        key = tuple(event.get("trial_key", []))
        if (event.get("run_id") != manifest["run_id"] or key not in expected or
                type(event.get("turn_index")) is not int or not 0 <= event["turn_index"] < 5):
            raise ValueError("unexpected current journal identity")
        request = event["request"] if event["event"] == "attempt" else event["record"]["request"]
        if request["model"] != key[0]:
            raise ValueError("journal model differs from trial")
    return results


def make_resume_plan(source=DEFAULT_SOURCE, histories=None):
    source = Path(source).resolve()
    histories = [Path(x).resolve() for x in (histories if histories is not None else [DEFAULT_HISTORY])]
    if source in histories or len(set(histories)) != len(histories):
        raise ValueError("duplicate source/history")
    config = pilot.load_config()
    manifest, rows, events = validate_source(source, config)
    known = uncertain = 0.0
    inputs = []
    for path in [*histories, source]:
        historic_manifest, _, historic_events = load_source(path)
        _, _, k, u = journal_attempts(historic_events, historic_manifest["plan"]["config"])
        known += k; uncertain += u
        totals = historic_manifest["totals"]["models"].values()
        if not math.isclose(k, sum(m["estimated_credits"] for m in totals), abs_tol=1e-10):
            raise ValueError("historical cost does not reconcile")
        inputs.append({"path": str(path), "files": {n: file_hash(path / n)
                       for n in ("manifest.json", "trials.jsonl", "calls.jsonl")}})
    complete = sum(r["failed_calls"] == 0 for r in rows)
    reusable_calls = sum(sum(not t["failed"] for t in r["turns"]) for r in rows)
    remaining_estimate = 0.0
    remaining_by_model = {}
    for model in config["models"]:
        reusable = sum(sum(not t["failed"] for t in r["turns"]) for r in rows if r["model"] == model["id"])
        count = len(config["seeds"]) * len(config["conditions"]) * len(config["authorizations"]) * 5 - reusable
        remaining_by_model[model["id"]] = count
        remaining_estimate += count * reservation({"model": model["id"], "max_output_tokens": config["max_output_tokens"]}, config)
    plan = {"config": config, "source": str(source), "histories": [str(x) for x in histories],
            "input_hashes": inputs, "completed_trials": complete,
            "remaining_trials": len(pilot.jobs(config)) - complete,
            "reusable_calls": reusable_calls, "remaining_calls_by_model": remaining_by_model,
            "remaining_single_attempt_planning_credits": remaining_estimate,
            "total_single_attempt_planning_credits": known + uncertain + remaining_estimate,
            "baseline_known_credits": known, "baseline_reserved_credits": uncertain,
            "credit_limit": config["max_credits"], "max_attempts_per_turn": MAX_ATTEMPTS,
            "retry_http_statuses": list(TRANSIENT_HTTP), "backoff_seconds": list(BACKOFF),
            "terminal_generation_failures": list(TERMINAL_GENERATION),
            "source_prompt_hash": manifest["prompt_hash"],
            "source_protocol_hash": manifest["protocol_hash"],
            "implementation_sha256": {n: file_hash(pilot.HERE / n)
                for n in (*pilot.SOURCE_FILES, "adaption_resume.py")},
            "derived_dataset": "One row per assigned trial, with explicit original run/protocol/row lineage; no frozen data pooled"}
    plan["approval_sha256"] = pilot.digest(plan)
    return plan


def retryable(record):
    return ((record.get("failure") == "http_error" and record.get("http_status") in TRANSIENT_HTTP)
            or (record.get("failure") == "transport_or_json_error" and record.get("retryable_transport") is True))


def record_text(record):
    raw = record.get("raw") or {}
    if (record.get("failure") is not None or raw.get("status") != "completed" or
            raw.get("error") is not None or raw.get("incomplete_details") is not None):
        raise ValueError("cached response is not successful")
    parts = []
    for item in raw.get("output") or []:
        if item.get("error") is not None or item.get("status") not in (None, "completed"):
            raise ValueError("cached output item is incomplete")
        if item.get("type") == "reasoning":
            continue
        if item.get("type") != "message" or item.get("role") != "assistant":
            raise ValueError("cached response contains a tool or invalid output")
        for part in item.get("content") or []:
            if (part.get("type") != "output_text" or not isinstance(part.get("text"), str) or
                    part.get("refusal") is not None or part.get("error") is not None):
                raise ValueError("cached response content is invalid")
            parts.append(part["text"])
    text = "".join(parts).strip()
    if not text:
        raise ValueError("cached response text is empty")
    return text


def collect_cache(source_rows, source_events, current_events):
    cache, old_attempts = {}, {}
    # Source results carry the original request/response and ordinal turn log.
    for row in source_rows:
        key = trial_key(row)
        broken = False
        for index, turn in enumerate(row["turns"]):
            record = turn["adaption"]
            logical = (key, index)
            if record["sent"]:
                old_attempts[logical] = [{"call_id": record["call_id"], "record": record, "request": record["request"],
                                          "run_id": row["run_id"]}]
            if turn["failed"]:
                broken = True
            elif broken:
                raise ValueError("source has successful turns after a failed prefix")
            else:
                cache[logical] = {"request": record["request"], "text": turn["raw"],
                                  "record": record, "source_turn": turn, "source_run_id": row["run_id"]}
    attempts, results, _, _ = journal_attempts(current_events, pilot.load_config())
    for call_id, attempt in attempts.items():
        key = tuple(attempt["trial_key"])
        logical = (key, attempt["turn_index"])
        result = results.get(call_id)
        record = result["record"] if result else None
        old_attempts.setdefault(logical, []).append({"call_id": call_id, "record": record, "request": attempt["request"],
                                                     "run_id": attempt["run_id"]})
        if record is not None and record["failure"] is None:
            if logical in cache:
                raise ValueError("duplicate successful logical turn")
            # Text extraction is the same accepted output-text contract as the backend.
            text = record_text(record)
            cache[logical] = {"request": attempt["request"], "text": text, "record": record,
                              "source_turn": None, "source_run_id": attempt["run_id"]}
    return cache, old_attempts


class ResumeBackend(h.Backend):
    def __init__(self, plan, key, output, context, source_rows, source_events, sleep):
        self._init_counters(cost=None)
        self.plan, self.key, self.output, self.context = plan, key, output, context
        self.sleep = sleep
        self.source_rows, self.source_events = source_rows, source_events
        self.index, self.used = 0, []
        self.terminal = False

    def failed_turn(self, record, reused=False, run_id=None):
        """run_id names the run whose journal holds the record (default: this continuation)."""
        self.terminal = True
        self.tl.model = [record["model"]] if record.get("model") else None
        self.used.append({"request": record["request"], "text": "PASS", "record": record, "source_turn": None,
                          "source_run_id": run_id or self.context["run_id"], "reused": reused})
        return self._fail(record["failure"])

    def __call__(self, system, user):
        index = self.index; self.index += 1
        config = self.plan["config"]
        expected = request_for(self.key[0], system, user, config)
        self.context.update(trial_key=list(self.key), turn_index=index)
        if self.terminal:
            record = {"call_id": str(uuid.uuid4()), "request": expected, "sent": False,
                      "failure": "trial_stopped", "raw": None, "raw_body": None, "model": None,
                      "http_status": None, "usage": None, "elapsed_ms": 0}
            append(self.output / "calls.jsonl", {**self.context, "event": "result",
                                                "call_id": record["call_id"], "record": record})
            return self.failed_turn(record)
        while True:
            events = read_jsonl(self.output / "calls.jsonl")
            cache, attempts = collect_cache(self.source_rows, self.source_events, events)
            logical = (self.key, index)
            history = attempts.get(logical, [])
            if any(item["request"] != expected for item in history):
                raise ValueError("reconstructed request differs from saved call")
            if logical in cache:
                saved = cache[logical]
                if saved["request"] != expected:
                    raise ValueError("replayed request differs from saved call")
                self.tl.model = [saved["record"]["model"]]
                self.used.append({**saved, "reused": True})
                return saved["text"]
            if history:
                last = history[-1]["record"]
                if last is not None and last.get("failure") in TERMINAL_GENERATION:
                    return self.failed_turn(last, reused=True, run_id=history[-1]["run_id"])
                if last is not None and not retryable(last):
                    raise RuntimeError("nonretryable prior turn failure; collection stopped")
                if len(history) >= MAX_ATTEMPTS:
                    raise RuntimeError("retry allowance exhausted for logical turn")
                self.sleep(BACKOFF[min(len(history) - 1, len(BACKOFF) - 1)])
            _, _, known, uncertain = journal_attempts(events, config)
            charged = self.plan["baseline_known_credits"] + self.plan["baseline_reserved_credits"] + known + uncertain
            available = self.plan["credit_limit"] - charged
            if available + 1e-12 < reservation(expected, config):
                raise RuntimeError("shared estimated credit limit reached")
            self.context.update(trial_key=list(self.key), turn_index=index)
            model = next(m for m in config["models"] if m["id"] == self.key[0])
            backend = api.Adaption(self.key[0], input_rate=model["input_credits_per_million"],
                                   output_rate=model["output_credits_per_million"], max_credits=available,
                                   max_output_tokens=config["max_output_tokens"], input_token_budget=config["input_token_budget"])
            backend.record_sink = lambda event: append(self.output / "calls.jsonl", {**self.context, **event})
            text = backend(system, user)
            record = backend.records[-1]
            if record["failure"] is None:
                self.tl.model = [record["model"]]
                self.used.append({"request": expected, "text": text, "record": record,
                                  "source_turn": None, "source_run_id": self.context["run_id"], "reused": False})
                return text
            if record["failure"] in TERMINAL_GENERATION:
                return self.failed_turn(record)
            if not retryable(record):
                raise RuntimeError("nonretryable backend failure: " + record["failure"])
            # Loop re-reads the durable journal; every failed send retains its own allowance.


def derived_row(row, manifest, source_path):
    result = copy.deepcopy(row)
    result.update(source_run_id=row["run_id"], source_protocol_hash=row["protocol_hash"],
                  source_row_sha256=pilot.digest(row), source_path=source_path,
                  source_phase=row["phase"], phase="exploratory-continuation",
                  run_id=manifest["run_id"], protocol_hash=manifest["protocol_hash"],
                  derived_analysis=True, continuation_execution_commit=manifest["git"]["commit"])
    return result


def reject_other_continuation(output, source_run_id):
    """Reject continuations under RESULTS, beside output, or claimed in RESULTS.

    The claim file (written under the pilot lock) catches out-of-tree outputs.
    It is per checkout, not a global registry."""
    for claim in read_jsonl(pilot.RESULTS / CLAIMS):
        if claim.get("source_run_id") == source_run_id and claim.get("output") != str(output):
            raise ValueError("another continuation for this source already exists: " + str(claim.get("output")))
    candidates = set(pilot.RESULTS.rglob("manifest.json"))
    candidates.update(output.parent.glob("*/manifest.json"))
    for path in candidates:
        if path.parent.resolve() == output:
            continue
        try:
            manifest = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if (isinstance(manifest, dict) and manifest.get("study") == pilot.STUDY and
                manifest.get("source_run_id") == source_run_id):
            raise ValueError("another continuation for this source already exists: " + str(path.parent))


def run_resume(plan, output, approval, *, sleep=time.sleep, amend=False):
    if make_resume_plan(plan["source"], plan["histories"]) != plan or approval != plan["approval_sha256"]:
        raise ValueError("stale or unapproved continuation plan")
    output = pilot.safe_output(output)
    roots = [Path(x["path"]) for x in plan["input_hashes"]]
    if any(output == root or root in output.parents or output in root.parents for root in roots):
        raise ValueError("continuation output must not overlap historical inputs")
    # This lock covers network requests as well as journal/row updates.
    pilot.RESULTS.mkdir(parents=True, exist_ok=True)
    with (pilot.RESULTS / ".resume.lock").open("a") as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise ValueError("another continuation holds the pilot lock") from None
        source_manifest, source_rows, source_events = validate_source(Path(plan["source"]), plan["config"])
        if not output.exists():
            reject_other_continuation(output, source_manifest["run_id"])
        if output.exists():
            manifest = json.loads((output / "manifest.json").read_text())
            if manifest["plan"] != plan:
                old = manifest["plan"]
                allowed = {"implementation_sha256", "approval_sha256", "terminal_generation_failures"}
                if (not amend or read_jsonl(output / "completed_trials.jsonl") or
                        {k: v for k, v in old.items() if k not in allowed} !=
                        {k: v for k, v in plan.items() if k not in allowed}):
                    raise ValueError("existing continuation has a different plan; unsafe amendment rejected")
                write_manifest(output / ("manifest.before-amendment-" + uuid.uuid4().hex + ".json"), manifest)
                append(output / "amendments.jsonl", {"at": h.now(), "old_plan": old, "new_plan": plan,
                                                    "reason": "record terminal generation failure and continue other assigned trials"})
                manifest.update(previous_protocol_hash=manifest["protocol_hash"], protocol_hash=pilot.digest(plan),
                                plan=plan, git=h.git_info())
                write_manifest(output / "manifest.json", manifest)
            read_jsonl(output / "calls.jsonl", recover=True)
            read_jsonl(output / "completed_trials.jsonl", recover=True)
        else:
            # Claim before creating output: a crash in between still blocks a second continuation.
            append(pilot.RESULTS / CLAIMS, {"source_run_id": source_manifest["run_id"], "output": str(output),
                                            "approval_sha256": plan["approval_sha256"], "at": h.now()})
            output.mkdir(parents=True, exist_ok=False)
            sync_directory(output.parent)
            manifest = {"study": pilot.STUDY, "phase": "exploratory-continuation", "run_id": str(uuid.uuid4()),
                        "protocol_hash": pilot.digest(plan), "prompt_hash": source_manifest["prompt_hash"],
                        "plan": plan, "git": h.git_info(), "start": h.now(), "end": None,
                        "status": "prepared", "source_run_id": source_manifest["run_id"], "totals": {}}
            write_manifest(output / "manifest.json", manifest)
        for name in ("calls.jsonl", "completed_trials.jsonl"):
            if not (output / name).exists():
                with (output / name).open("x") as stream:
                    stream.flush(); os.fsync(stream.fileno())
        sync_directory(output)
        original = [r for r in source_rows if r["failed_calls"] == 0]
        completed = read_jsonl(output / "completed_trials.jsonl")
        source_keys = {trial_key(r) for r in original}
        new_keys = [trial_key(r) for r in completed]
        expected = {(m["id"], s, c, a) for m, s, c, a in pilot.jobs(plan["config"])}
        if len(set(new_keys)) != len(new_keys) or source_keys.intersection(new_keys) or not set(new_keys) <= expected:
            raise ValueError("duplicate or unexpected completed trial")
        events = read_jsonl(output / "calls.jsonl")
        current_results = validate_current(events, manifest, expected, plan["config"])
        _, source_results, _, _ = journal_attempts(source_events, plan["config"])
        for row in completed:
            if row["run_id"] != manifest["run_id"] or row["protocol_hash"] != manifest["protocol_hash"]:
                raise ValueError("invalid continuation trial identity")
            validate_trial(row, plan["config"], {**source_results, **current_results})
        # Validate current call history before accessing credentials/network.
        collect_cache(source_rows, source_events, read_jsonl(output / "calls.jsonl"))
        done = source_keys | set(new_keys)
        manifest["status"] = "running"
        manifest.pop("stop_reason", None)
        write_manifest(output / "manifest.json", manifest)
        context = {"run_id": manifest["run_id"]}
        try:
            if done != expected:
                pilot.preflight_models(plan["config"])
            for model, seed, condition, authorization in pilot.jobs(plan["config"]):
                key = (model["id"], seed, condition, authorization)
                if key in done:
                    continue
                backend = ResumeBackend(plan, key, output, context, source_rows, source_events, sleep)
                row = p.run_trial(backend, seed, condition, authorization, plan["config"]["wording"])
                row.update(study=pilot.STUDY, design=pilot.STUDY, backend="adaption", model=model["id"],
                           requested_model=model["id"], phase="exploratory-continuation", mock_only=False,
                           run_id=manifest["run_id"], prompt_hash=manifest["prompt_hash"], protocol_hash=manifest["protocol_hash"],
                           source_design=p.STUDY, continuation_execution_commit=manifest["git"]["commit"])
                prior = next((r for r in source_rows if trial_key(r) == key), None)
                if prior is not None:
                    row.update(replaces_failed_source_row=True, source_run_id=prior["run_id"],
                               source_protocol_hash=prior["protocol_hash"], source_row_sha256=pilot.digest(prior),
                               source_path=plan["source"])
                for turn, used in zip(row["turns"], backend.used):
                    turn.update(adaption=used["record"], reused=used["reused"], source_run_id=used["source_run_id"])
                    if used["source_turn"]:
                        turn["ms"] = used["source_turn"]["ms"]
                    elif used["reused"]:
                        turn["ms"] = used["record"]["elapsed_ms"]
                _, attempted = collect_cache(source_rows, source_events, read_jsonl(output / "calls.jsonl"))
                for index, turn in enumerate(row["turns"]):
                    turn["attempt_call_ids"] = [a["call_id"] for a in attempted.get((key, index), [])]
                if len(backend.used) != 5:
                    raise RuntimeError("trial is incomplete")
                append(output / "completed_trials.jsonl", row)
                completed.append(row); done.add(key)
            manifest["status"] = "complete"
        except BaseException as error:
            manifest["status"] = "stopped: " + type(error).__name__
            manifest["stop_reason"] = str(error) if isinstance(error, (RuntimeError, ValueError)) else type(error).__name__
            raise
        finally:
            events = read_jsonl(output / "calls.jsonl", recover=True)
            attempts, results, known, uncertain = journal_attempts(events, plan["config"])
            combined = [derived_row(r, manifest, plan["source"]) for r in original] + completed
            analyze.validate_rows(combined, analyze.DEFAULT_BY)
            atomic_jsonl(output / "combined_trials.jsonl", combined)
            manifest.update(end=h.now(), totals={"completed_trials": len(combined), "preserved_trials": len(original),
                            "valid_trials": sum(r["failed_calls"] == 0 for r in combined),
                            "failed_trials": sum(r["failed_calls"] > 0 for r in combined),
                            "new_trials": len(completed), "new_post_attempts": len(attempts),
                            "new_known_credits": known, "new_reserved_credits": uncertain,
                            "total_known_credits": plan["baseline_known_credits"] + known,
                            "total_reserved_credits": plan["baseline_reserved_credits"] + uncertain})
            write_manifest(output / "manifest.json", manifest)
        return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--history", type=Path, action="append")
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--amend-execution", action="store_true")
    args = parser.parse_args(argv)
    plan = make_resume_plan(args.source, args.history)
    if not args.execute:
        print(json.dumps(plan, indent=2, sort_keys=True)); return 0
    if args.out_dir is None: parser.error("--out-dir is required")
    result = run_resume(plan, args.out_dir, args.approve_plan, amend=args.amend_execution)
    print(json.dumps(result["totals"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
