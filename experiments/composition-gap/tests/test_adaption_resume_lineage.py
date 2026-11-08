"""Offline tests for continuation lineage and the per-source continuation claim."""
import json
import shutil
from pathlib import Path

import pytest

import adaption_backend as backend
import adaption_pilot as pilot
import adaption_resume as resume


HERE = Path(__file__).resolve().parents[1]
RESULTS = HERE / "results" / pilot.STUDY


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def save_rows(path, entries):
    path.write_text("".join(json.dumps(entry) + "\n" for entry in entries))


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


def install_fake(monkeypatch):
    monkeypatch.setattr(pilot, "preflight_models", lambda config: [m["id"] for m in config["models"]])
    monkeypatch.setenv("ADAPTION_API_KEY", "offline-test-key")
    sent = []

    def send(request, timeout):
        payload = json.loads(request.data)
        sent.append(payload)
        return Response(payload)

    monkeypatch.setattr(backend.urllib.request, "urlopen", send)
    return sent


def deny_network(monkeypatch):
    monkeypatch.setattr(pilot, "preflight_models", lambda *_: pytest.fail("preflight"))
    monkeypatch.setattr(backend.urllib.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("network"))


def make_source_failure_terminal(source):
    """Turn the source's last sent failure (a 504) into a terminal generation failure."""
    trials = rows(source / "trials.jsonl")
    turn = trials[-1]["turns"][2]
    assert turn["failed"] and turn["adaption"]["sent"] and turn["adaption"]["failure"] == "http_error"
    turn["adaption"].update(failure="status_not_completed", http_status=200)
    turn["fail_reason"] = "status_not_completed"
    events = rows(source / "calls.jsonl")
    result = next(e for e in events if e["event"] == "result" and e["call_id"] == turn["adaption"]["call_id"])
    result["record"] = turn["adaption"]
    save_rows(source / "trials.jsonl", trials)
    save_rows(source / "calls.jsonl", events)
    return trials[-1], turn["adaption"]["call_id"]


def test_reused_source_terminal_failure_keeps_source_lineage(tmp_path, sources, monkeypatch):
    first, second = sources
    source_row, failed_call_id = make_source_failure_terminal(second)
    plan = resume.make_resume_plan(second, [first])
    sent = install_fake(monkeypatch)
    out = tmp_path / "resume"
    manifest = resume.run_resume(plan, out, plan["approval_sha256"], sleep=lambda _: None)
    assert manifest["status"] == "complete"
    # The terminal failure is reused, not resent; its trial stops there.
    assert len(sent) == 18 * 5
    repaired = next(r for r in rows(out / "completed_trials.jsonl")
                    if resume.trial_key(r) == resume.trial_key(source_row))
    turn = repaired["turns"][2]
    assert turn["reused"] and turn["adaption"]["call_id"] == failed_call_id
    assert turn["source_run_id"] == source_row["run_id"] != manifest["run_id"]
    # Turns stopped by the continuation itself belong to the continuation.
    assert [t["source_run_id"] for t in repaired["turns"][3:]] == [manifest["run_id"]] * 2


def test_second_out_of_tree_continuation_is_rejected_by_claim(tmp_path, sources, monkeypatch):
    first, second = sources
    plan = resume.make_resume_plan(second, [first])
    install_fake(monkeypatch)
    one = tmp_path / "elsewhere-a" / "continuation"
    resume.run_resume(plan, one, plan["approval_sha256"], sleep=lambda _: None)
    deny_network(monkeypatch)
    # Neither under RESULTS nor a sibling of the first output: only the claim can see it.
    two = tmp_path / "elsewhere-b" / "continuation"
    with pytest.raises(ValueError, match="another continuation"):
        resume.run_resume(plan, two, plan["approval_sha256"], sleep=lambda _: None)
    assert not two.exists()
    # Restarting the claimed output is still allowed.
    result = resume.run_resume(plan, one, plan["approval_sha256"], sleep=lambda _: None)
    assert result["status"] == "complete"
