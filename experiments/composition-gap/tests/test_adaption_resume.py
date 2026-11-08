"""Offline regression tests for recovery of the interrupted Adaption pilot."""
import copy
import fcntl
import io
import json
import shutil
from pathlib import Path
from urllib.error import HTTPError

import pytest

import adaption_backend as backend
import adaption_pilot as pilot
import adaption_resume as resume


HERE = Path(__file__).resolve().parents[1]
RESULTS = HERE / "results" / pilot.STUDY


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


@pytest.fixture(autouse=True)
def isolated_results_root(tmp_path, monkeypatch):
    # The real archived continuation must not interfere with copied test sources.
    monkeypatch.setattr(pilot, "RESULTS", tmp_path / "isolated-results")


@pytest.fixture
def sources(tmp_path):
    first, second = tmp_path / "pilot-01", tmp_path / "pilot-02"
    shutil.copytree(RESULTS / "pilot-01", first)
    shutil.copytree(RESULTS / "pilot-02", second)
    return first, second


@pytest.fixture
def plan(sources):
    first, second = sources
    return resume.make_resume_plan(second, [first])


class Response:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"id": "fake-response", "model": self.payload["model"],
                           "status": "completed", "error": None, "incomplete_details": None,
                           "usage": {"input_tokens": 100, "output_tokens": 2},
                           "output": [{"type": "message", "role": "assistant", "content": [
                               {"type": "output_text", "text": "PASS"}]}]}).encode()


def approve(plan):
    return plan["approval_sha256"]


def install_fake(monkeypatch, effects=()):
    monkeypatch.setattr(pilot, "preflight_models", lambda config: [m["id"] for m in config["models"]])
    monkeypatch.setenv("ADAPTION_API_KEY", "offline-test-key")
    sent = []
    effects = iter(effects)

    def send(request, timeout):
        payload = json.loads(request.data)
        sent.append(payload)
        effect = next(effects, None)
        if isinstance(effect, BaseException):
            raise effect
        return effect if effect is not None else Response(payload)

    monkeypatch.setattr(backend.urllib.request, "urlopen", send)
    return sent


def http_error(status):
    return HTTPError(backend.ENDPOINT, status, "fake error", {}, io.BytesIO(b"fake error"))


def test_plan_accounts_for_both_original_runs_and_preserves_sources(sources, plan, monkeypatch):
    monkeypatch.setattr(backend.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network during planning"))
    first, second = sources
    before = {p: p.read_bytes() for d in sources for p in d.iterdir() if p.is_file()}
    again = resume.make_resume_plan(second, [first])
    assert again == plan
    assert plan["completed_trials"] == 5
    assert plan["remaining_trials"] == 19
    assert plan["baseline_known_credits"] == pytest.approx(.0660275)
    assert plan["baseline_reserved_credits"] == pytest.approx(.015711)
    assert {p: p.read_bytes() for p in before} == before


def test_complete_resume_replays_only_failed_turn_and_derives_24_unique_rows(tmp_path, sources, plan, monkeypatch):
    sent = install_fake(monkeypatch)
    original = rows(sources[1] / "trials.jsonl")
    old = {p: p.read_bytes() for d in sources for p in d.iterdir() if p.is_file()}
    out = tmp_path / "resume"
    manifest = resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    assert manifest["status"] == "complete"
    # Five complete trials and the first two successful turns of the partial trial are reused.
    assert len(sent) == 19 * 5 - 2
    assert sent[0] == original[-1]["turns"][2]["adaption"]["request"]
    new = rows(out / "completed_trials.jsonl")
    combined = rows(out / "combined_trials.jsonl")
    assert len(new) == 19 and len(combined) == 24
    assert len({resume.trial_key(r) for r in combined}) == 24
    assert {resume.trial_key(r) for r in original if r["valid"]}.isdisjoint(
        {resume.trial_key(r) for r in new})
    assert sum(bool(r.get("derived_analysis")) for r in combined) == 5
    repaired = [r for r in combined if r.get("replaces_failed_source_row")]
    assert len(repaired) == 1 and repaired[0]["source_run_id"] == original[-1]["run_id"]
    assert repaired[0]["source_protocol_hash"] == original[-1]["protocol_hash"]
    assert repaired[0]["source_row_sha256"] == pilot.digest(original[-1])
    assert all(t.get("source_run_id") for r in new for t in r["turns"])
    assert all(r["valid"] for r in combined)
    assert {p: p.read_bytes() for p in old} == old


def test_504_retry_uses_identical_request_and_counts_original_attempt(tmp_path, plan, monkeypatch):
    sent = install_fake(monkeypatch, [http_error(504)])
    waits = []
    manifest = resume.run_resume(plan, tmp_path / "retry", approve(plan), sleep=waits.append)
    assert manifest["status"] == "complete"
    assert sent[0] == sent[1]
    assert len(sent) == 94
    assert waits == [5, 15]


@pytest.mark.parametrize("effect", [http_error(502), http_error(503), TimeoutError("timed out")],
                         ids=["502", "503", "transport-timeout"])
def test_transient_failure_is_retried_with_identical_request(tmp_path, plan, monkeypatch, effect):
    sent = install_fake(monkeypatch, [effect])
    manifest = resume.run_resume(plan, tmp_path / "transient", approve(plan), sleep=lambda _: None)
    assert manifest["status"] == "complete"
    assert sent[0] == sent[1]
    assert len(sent) == 94


def test_original_504_and_two_more_504s_stop_at_three_attempts(tmp_path, plan, monkeypatch):
    sent = install_fake(monkeypatch, [http_error(504), http_error(504), http_error(504)])
    with pytest.raises(RuntimeError, match="exhausted"):
        resume.run_resume(plan, tmp_path / "limit", approve(plan), sleep=lambda _: None)
    assert len(sent) == 2
    assert sent[0] == sent[1]


@pytest.mark.parametrize("effect", [http_error(400), http_error(401), http_error(429), http_error(500)])
def test_permanent_http_failure_is_not_retried(tmp_path, plan, monkeypatch, effect):
    sent = install_fake(monkeypatch, [effect])
    with pytest.raises(RuntimeError, match="nonretryable"):
        resume.run_resume(plan, tmp_path / "permanent", approve(plan), sleep=lambda _: None)
    assert len(sent) == 1


def test_malformed_success_is_not_retried(tmp_path, plan, monkeypatch):
    class Malformed:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b"not JSON"
    sent = install_fake(monkeypatch, [Malformed()])
    with pytest.raises(RuntimeError, match="nonretryable"):
        resume.run_resume(plan, tmp_path / "malformed", approve(plan), sleep=lambda _: None)
    assert len(sent) == 1


def test_duplicate_or_conflicting_completed_source_rows_are_rejected(sources):
    first, second = sources
    path = second / "trials.jsonl"
    duplicate = rows(path)[0]
    with path.open("a") as f:
        f.write(json.dumps(duplicate) + "\n")
    with pytest.raises(ValueError):
        resume.make_resume_plan(second, [first])


def test_changed_source_after_planning_rejected_before_network(tmp_path, sources, plan, monkeypatch):
    sent = install_fake(monkeypatch)
    path = sources[1] / "trials.jsonl"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError):
        resume.run_resume(plan, tmp_path / "stale", approve(plan), sleep=lambda _: None)
    assert not sent


@pytest.mark.parametrize("drift", ["code-changed-after-approval", "plan-edited-and-resigned"])
def test_approved_plan_that_no_longer_matches_inputs_is_stale(tmp_path, plan, monkeypatch, drift):
    # Sources stay readable and valid, so only the recomputed-plan comparison can reject this.
    sent = install_fake(monkeypatch)
    approved = copy.deepcopy(plan)
    if drift == "code-changed-after-approval":
        real_hash = resume.file_hash
        monkeypatch.setattr(resume, "file_hash",
                            lambda path: "0" * 64 if Path(path).name == "adaption_resume.py" else real_hash(path))
    else:
        approved["baseline_known_credits"] = 0.0
        approved.pop("approval_sha256")
        approved["approval_sha256"] = pilot.digest(approved)
    out = tmp_path / "stale-plan"
    with pytest.raises(ValueError, match="stale or unapproved"):
        resume.run_resume(approved, out, approve(approved), sleep=lambda _: None)
    assert not sent
    assert not out.exists()


def test_held_pilot_lock_rejects_continuation_before_network(tmp_path, plan, monkeypatch):
    sent = install_fake(monkeypatch)
    pilot.RESULTS.mkdir(parents=True)
    out = tmp_path / "locked"
    with (pilot.RESULTS / ".resume.lock").open("a") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match="another continuation holds the pilot lock"):
            resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    assert not sent
    assert not out.exists()


def unstarted_trial_backend(tmp_path, sources, plan):
    _, source_rows, source_events = resume.load_source(sources[1])
    started = {resume.trial_key(r) for r in source_rows}
    key = next((m["id"], s, c, a) for m, s, c, a in pilot.jobs(plan["config"])
               if (m["id"], s, c, a) not in started)
    out = tmp_path / "direct"
    out.mkdir()
    rb = resume.ResumeBackend(plan, key, out, {"run_id": "direct-test"}, source_rows, source_events,
                              sleep=lambda _: None)
    return rb, key, out


def test_shared_credit_gate_stops_before_any_send(tmp_path, sources, plan, monkeypatch):
    sent = install_fake(monkeypatch)
    near_limit = copy.deepcopy(plan)
    rb, key, out = unstarted_trial_backend(tmp_path, sources, near_limit)
    one = resume.reservation(resume.request_for(key[0], "system", "user", plan["config"]), plan["config"])
    # Leave half of one reservation: positive, but not enough for another send.
    near_limit["baseline_known_credits"] = plan["credit_limit"] - plan["baseline_reserved_credits"] - one / 2
    with pytest.raises(RuntimeError, match="shared estimated credit limit reached"):
        rb("system", "user")
    assert not sent
    assert not (out / "calls.jsonl").exists()


def test_backend_budget_is_the_remaining_shared_allowance(tmp_path, sources, plan, monkeypatch):
    sent = install_fake(monkeypatch)
    budgets = []
    original = backend.Adaption
    class Spy(original):
        def __init__(self, *args, **kwargs):
            budgets.append(kwargs["max_credits"])
            super().__init__(*args, **kwargs)
    monkeypatch.setattr(backend, "Adaption", Spy)
    rb, _, out = unstarted_trial_backend(tmp_path, sources, plan)
    assert rb("system", "first") == "PASS"
    assert rb("system", "second") == "PASS"
    first_cost = next(e for e in rows(out / "calls.jsonl") if e["event"] == "result")["record"]["estimated_credits"]
    remaining = plan["credit_limit"] - plan["baseline_known_credits"] - plan["baseline_reserved_credits"]
    assert first_cost > 0
    assert budgets == [pytest.approx(remaining, abs=1e-12), pytest.approx(remaining - first_cost, abs=1e-12)]
    assert len(sent) == 2


def test_bad_approval_rejected_before_preflight_or_output(tmp_path, plan, monkeypatch):
    monkeypatch.setattr(pilot, "preflight_models", lambda *_: pytest.fail("preflight before approval"))
    out = tmp_path / "unapproved"
    with pytest.raises(ValueError):
        resume.run_resume(plan, out, "incorrect", sleep=lambda _: None)
    assert not out.exists()


def test_conflicting_duplicate_source_rows_are_rejected(sources):
    first, second = sources
    path = second / "trials.jsonl"
    duplicate = copy.deepcopy(rows(path)[0])
    duplicate["board"] = [{"actor": "conflict", "text": "conflict"}]
    with path.open("a") as f:
        f.write(json.dumps(duplicate) + "\n")
    with pytest.raises(ValueError):
        resume.make_resume_plan(second, [first])


def test_interrupted_attempt_keeps_reservation_and_restart_reuses_successes(tmp_path, plan, monkeypatch):
    sent = install_fake(monkeypatch, [None] * 5 + [KeyboardInterrupt()])
    out = tmp_path / "interrupted"
    with pytest.raises(KeyboardInterrupt):
        resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    interrupted = json.loads((out / "manifest.json").read_text())
    journal = rows(out / "calls.jsonl")
    assert journal[-1]["event"] == "attempt"
    # Exactly the one unresolved send stays reserved; the five answered sends are known costs.
    one = resume.reservation(journal[-1]["request"], plan["config"])
    assert interrupted["totals"]["new_reserved_credits"] == pytest.approx(one, abs=1e-12)
    assert interrupted["totals"]["total_reserved_credits"] == pytest.approx(
        plan["baseline_reserved_credits"] + one, abs=1e-12)
    assert len(rows(out / "completed_trials.jsonl")) == 1
    sent_before = list(sent)
    resumed = install_fake(monkeypatch)
    manifest = resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    assert manifest["status"] == "complete"
    assert resumed[0] == sent_before[-1]
    assert len(resumed) == 93 - 5
    assert len(rows(out / "completed_trials.jsonl")) == 19
    assert len({resume.trial_key(r) for r in rows(out / "combined_trials.jsonl")}) == 24
    assert manifest["totals"]["new_reserved_credits"] == pytest.approx(one, abs=1e-12)


def interrupted_run(tmp_path, plan, monkeypatch):
    install_fake(monkeypatch, [None] * 5 + [KeyboardInterrupt()])
    out = tmp_path / "interrupted-integrity"
    with pytest.raises(KeyboardInterrupt):
        resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    return out


def deny_preflight(monkeypatch):
    monkeypatch.setattr(pilot, "preflight_models", lambda *_: pytest.fail("preflight before integrity check"))
    monkeypatch.setattr(backend.urllib.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("network"))


def save_rows(path, entries):
    path.write_text("".join(json.dumps(entry) + "\n" for entry in entries))


@pytest.mark.parametrize("corruption", ["context", "cost"])
def test_tampered_current_journal_rejected_before_preflight(tmp_path, plan, monkeypatch, corruption):
    out = interrupted_run(tmp_path, plan, monkeypatch)
    path = out / "calls.jsonl"
    events = rows(path)
    result = next(event for event in events if event["event"] == "result")
    if corruption == "context":
        result["turn_index"] += 1
    else:
        result["record"]["estimated_credits"] = 0
    save_rows(path, events)
    deny_preflight(monkeypatch)
    with pytest.raises(ValueError):
        resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)


def test_recovery_adds_newline_after_complete_json_tail(tmp_path):
    path = tmp_path / "calls.jsonl"
    path.write_bytes(b'{"first": 1}\n{"second": 2}')
    assert resume.read_jsonl(path, recover=True) == [{"first": 1}, {"second": 2}]
    resume.append(path, {"third": 3})
    assert rows(path) == [{"first": 1}, {"second": 2}, {"third": 3}]
    assert not list(tmp_path.glob("*.interrupted-*"))


def test_tampered_completed_row_rejected_before_preflight(tmp_path, plan, monkeypatch):
    out = interrupted_run(tmp_path, plan, monkeypatch)
    path = out / "completed_trials.jsonl"
    completed = rows(path)
    completed[0]["turns"][0]["raw"] = "POST: tampered"
    save_rows(path, completed)
    deny_preflight(monkeypatch)
    with pytest.raises(ValueError):
        resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)


class IncompleteResponse(Response):
    def read(self):
        return json.dumps({"id": "incomplete", "model": self.payload["model"],
                           "status": "incomplete", "error": None,
                           "incomplete_details": {"reason": "max_output_tokens"},
                           "usage": {"input_tokens": 100, "output_tokens": 4096},
                           "output": []}).encode()


class IncompleteDetailsResponse(Response):
    def read(self):
        value = json.loads(super().read())
        value["incomplete_details"] = {"reason": "content_filter"}
        return json.dumps(value).encode()


class EmptyOutputResponse(Response):
    def read(self):
        value = json.loads(super().read())
        value["output"][0]["content"][0]["text"] = "  "
        return json.dumps(value).encode()


@pytest.mark.parametrize("terminal, reason", [(IncompleteResponse, "status_not_completed"),
                                              (IncompleteDetailsResponse, "incomplete"),
                                              (EmptyOutputResponse, "empty_output")])
def test_incomplete_generation_records_failed_trial_without_resampling(tmp_path, plan, monkeypatch, terminal, reason):
    monkeypatch.setattr(pilot, "preflight_models", lambda config: [m["id"] for m in config["models"]])
    monkeypatch.setenv("ADAPTION_API_KEY", "offline-test-key")
    sent = []
    def send(request, timeout):
        payload = json.loads(request.data)
        sent.append(payload)
        return terminal(payload) if len(sent) == 1 else Response(payload)
    monkeypatch.setattr(backend.urllib.request, "urlopen", send)
    out = tmp_path / "incomplete"
    manifest = resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    combined = rows(out / "combined_trials.jsonl")
    assert manifest["status"] == "complete"
    assert len(sent) == 91  # Two remaining turns of the failed trial are not sent.
    assert len(combined) == 24
    assert len({resume.trial_key(row) for row in combined}) == 24
    failed = [row for row in combined if not row["valid"]]
    assert len(failed) == 1 and failed[0]["replaces_failed_source_row"]
    assert [t["fail_reason"] for t in failed[0]["turns"]][2:] == [reason, "trial_stopped", "trial_stopped"]
    assert sum(row["valid"] for row in combined) == 23
    assert sent.count(sent[0]) == 1
    assert sum(e["event"] == "attempt" for e in rows(out / "calls.jsonl")) == 91
    deny_preflight(monkeypatch)
    resumed = resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    assert resumed["status"] == "complete"
    assert len(rows(out / "combined_trials.jsonl")) == 24


def setup_old_plan_output(tmp_path, plan, monkeypatch):
    install_fake(monkeypatch, [KeyboardInterrupt()])
    out = tmp_path / "amend"
    with pytest.raises(KeyboardInterrupt):
        resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    path = out / "manifest.json"
    manifest = json.loads(path.read_text())
    old = copy.deepcopy(manifest["plan"])
    old["implementation_sha256"]["adaption_resume.py"] = "0" * 64
    old.pop("terminal_generation_failures", None)
    old.pop("approval_sha256")
    old["approval_sha256"] = pilot.digest(old)
    manifest["plan"] = old
    resume.write_manifest(path, manifest)
    return out, old


def test_code_policy_amendment_preserves_journal_and_reservations(tmp_path, plan, monkeypatch):
    out, old = setup_old_plan_output(tmp_path, plan, monkeypatch)
    journal_before = (out / "calls.jsonl").read_bytes()
    old_manifest = json.loads((out / "manifest.json").read_text())
    sent = install_fake(monkeypatch)
    result = resume.run_resume(plan, out, approve(plan), sleep=lambda _: None, amend=True)
    assert result["status"] == "complete"
    assert (out / "calls.jsonl").read_bytes().startswith(journal_before)
    # The interrupted first send keeps its single reservation through amendment and completion.
    interrupted_request = json.loads(journal_before.splitlines()[0])["request"]
    one = resume.reservation(interrupted_request, plan["config"])
    assert old_manifest["totals"]["new_reserved_credits"] == pytest.approx(one, abs=1e-12)
    assert result["totals"]["new_reserved_credits"] == pytest.approx(one, abs=1e-12)
    assert len(sent) == 93
    assert old["approval_sha256"] != approve(plan)
    archives = list(out.glob("manifest.before-amendment-*.json"))
    assert len(archives) == 1
    assert json.loads(archives[0].read_text())["plan"] == old
    amendments = rows(out / "amendments.jsonl")
    assert len(amendments) == 1 and amendments[0]["old_plan"] == old
    assert amendments[0]["new_plan"] == plan


def test_amendment_rejects_changed_configuration_before_preflight(tmp_path, plan, monkeypatch):
    out, _ = setup_old_plan_output(tmp_path, plan, monkeypatch)
    path = out / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["plan"]["config"]["max_credits"] = 1
    resume.write_manifest(path, manifest)
    before = (out / "calls.jsonl").read_bytes()
    deny_preflight(monkeypatch)
    with pytest.raises(ValueError):
        resume.run_resume(plan, out, approve(plan), sleep=lambda _: None, amend=True)
    assert (out / "calls.jsonl").read_bytes() == before


def test_amendment_rejects_output_with_completed_rows(tmp_path, plan, monkeypatch):
    out = interrupted_run(tmp_path, plan, monkeypatch)
    path = out / "manifest.json"
    manifest = json.loads(path.read_text())
    old = manifest["plan"]
    old["implementation_sha256"]["adaption_resume.py"] = "0" * 64
    old.pop("terminal_generation_failures", None)
    old.pop("approval_sha256")
    old["approval_sha256"] = pilot.digest(old)
    resume.write_manifest(path, manifest)
    deny_preflight(monkeypatch)
    with pytest.raises(ValueError, match="amendment"):
        resume.run_resume(plan, out, approve(plan), sleep=lambda _: None, amend=True)


@pytest.mark.parametrize("unmatched_attempt", [False, True])
def test_source_journal_without_trial_fails_before_preflight(sources, monkeypatch, unmatched_attempt):
    first, second = sources
    trials = rows(second / "trials.jsonl")
    missing = trials.pop()
    save_rows(second / "trials.jsonl", trials)
    events = rows(second / "calls.jsonl")
    if unmatched_attempt:
        successful_id = missing["turns"][0]["adaption"]["call_id"]
        events = [e for e in events if not (e["event"] == "result" and e["call_id"] == successful_id)]
        save_rows(second / "calls.jsonl", events)
    before = {p: p.read_bytes() for d in sources for p in d.iterdir() if p.is_file()}
    monkeypatch.delenv("ADAPTION_API_KEY", raising=False)
    deny_preflight(monkeypatch)
    with pytest.raises(ValueError, match="without a saved trial"):
        resume.make_resume_plan(second, [first])
    assert {p: p.read_bytes() for p in before} == before


def test_second_continuation_rejected_but_same_output_restart_allowed(tmp_path, plan, monkeypatch):
    first = interrupted_run(tmp_path, plan, monkeypatch)
    deny_preflight(monkeypatch)
    second = tmp_path / "other-continuation"
    with pytest.raises(ValueError, match="another continuation"):
        resume.run_resume(plan, second, approve(plan), sleep=lambda _: None)
    assert not second.exists()
    sent = install_fake(monkeypatch)
    result = resume.run_resume(plan, first, approve(plan), sleep=lambda _: None)
    assert result["status"] == "complete"
    assert len(sent) == 88


@pytest.fixture
def published_trial():
    root = RESULTS / "pilot-03-resume"
    manifest = json.loads((root / "manifest.json").read_text())
    config = manifest["plan"]["config"]
    row = rows(root / "combined_trials.jsonl")[5]
    _, source_results, _, _ = resume.journal_attempts(rows(RESULTS / "pilot-02" / "calls.jsonl"), config)
    _, current, _, _ = resume.journal_attempts(rows(root / "calls.jsonl"), config)
    return row, config, {**source_results, **current}


def tamper_turn(row, results, index, **changes):
    row = copy.deepcopy(row)
    turn = row["turns"][index]
    turn.update({k: v for k, v in changes.items() if k in turn})
    record = turn["adaption"] = {**turn["adaption"], **changes.get("record", {})}
    return row, {**results, record["call_id"]: {**results[record["call_id"]], "record": record}}


def test_published_failed_turns_validate(published_trial):
    row, config, results = published_trial
    assert {t["fail_reason"] for t in row["turns"] if t["failed"]} == {"status_not_completed", "trial_stopped"}
    resume.validate_trial(row, config, results)


def test_successful_turn_flipped_to_failed_is_rejected(published_trial):
    row, config, results = published_trial
    assert not row["turns"][0]["failed"] and row["turns"][0]["adaption"]["failure"] is None
    row, results = tamper_turn(row, results, 0, failed=True)
    with pytest.raises(ValueError, match="failed turn lacks a matching terminal failure record"):
        resume.validate_trial(row, config, results)


def test_failed_turn_with_mismatched_fail_reason_is_rejected(published_trial):
    row, config, results = published_trial
    row, results = tamper_turn(row, results, 2, fail_reason="empty_output")
    with pytest.raises(ValueError, match="failed turn lacks a matching terminal failure record"):
        resume.validate_trial(row, config, results)


def test_failed_turn_with_transient_record_failure_is_rejected(published_trial):
    row, config, results = published_trial
    row, results = tamper_turn(row, results, 2, fail_reason="http_error", record={"failure": "http_error"})
    with pytest.raises(ValueError, match="failed turn lacks a matching terminal failure record"):
        resume.validate_trial(row, config, results)
