"""Offline regression tests for recovery of the interrupted Adaption pilot."""
import copy
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


def test_original_504_and_two_more_504s_stop_at_three_attempts(tmp_path, plan, monkeypatch):
    sent = install_fake(monkeypatch, [http_error(504), http_error(504), http_error(504)])
    with pytest.raises(RuntimeError, match="exhausted"):
        resume.run_resume(plan, tmp_path / "limit", approve(plan), sleep=lambda _: None)
    assert len(sent) == 2
    assert sent[0] == sent[1]


@pytest.mark.parametrize("effect", [http_error(400), http_error(401)])
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
    assert interrupted["totals"]["new_reserved_credits"] > 0
    assert interrupted["totals"]["total_reserved_credits"] > plan["baseline_reserved_credits"]
    assert len(rows(out / "completed_trials.jsonl")) == 1
    sent_before = list(sent)
    resumed = install_fake(monkeypatch)
    manifest = resume.run_resume(plan, out, approve(plan), sleep=lambda _: None)
    assert manifest["status"] == "complete"
    assert resumed[0] == sent_before[-1]
    assert len(resumed) == 93 - 5
    assert len(rows(out / "completed_trials.jsonl")) == 19
    assert len({resume.trial_key(r) for r in rows(out / "combined_trials.jsonl")}) == 24
    assert manifest["totals"]["new_reserved_credits"] >= interrupted["totals"]["new_reserved_credits"]


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


def test_incomplete_generation_records_failed_trial_without_resampling(tmp_path, plan, monkeypatch):
    monkeypatch.setattr(pilot, "preflight_models", lambda config: [m["id"] for m in config["models"]])
    monkeypatch.setenv("ADAPTION_API_KEY", "offline-test-key")
    sent = []
    def send(request, timeout):
        payload = json.loads(request.data)
        sent.append(payload)
        return IncompleteResponse(payload) if len(sent) == 1 else Response(payload)
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
    assert result["totals"]["new_reserved_credits"] >= old_manifest["totals"]["new_reserved_credits"]
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
