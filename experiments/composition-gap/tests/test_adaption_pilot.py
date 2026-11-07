"""Offline checks for the separate Adaption pilot and its approval boundary."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

import adaption_backend as backend
import adaption_pilot as pilot
import analyze


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_default_plan_is_offline_and_has_reviewable_costs(monkeypatch, capsys):
    monkeypatch.delenv("ADAPTION_API_KEY", raising=False)
    monkeypatch.setattr(pilot.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network on plan"))
    assert pilot.main([]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["trials"] == 24 and plan["logical_calls"] == 120
    assert plan["expected_credits"] == pytest.approx(0.08832)
    assert plan["planning_credits"] == pytest.approx(0.16512)
    assert plan["config"]["max_credits"] == 0.25
    assert plan["approval_sha256"] == pilot.digest({k: v for k, v in plan.items() if k != "approval_sha256"})
    for name, value in plan["source_files_sha256"].items():
        assert value == hashlib.sha256((pilot.HERE / name).read_bytes()).hexdigest()


@pytest.mark.parametrize("seeds", [[3000], [4999], [5000, 5000]])
def test_invalid_or_frozen_seeds_are_rejected(tmp_path, seeds):
    config = pilot.load_config()
    config["seeds"] = seeds
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="seeds"):
        pilot.load_config(path)


def test_seed_overlap_with_existing_results_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "HERE", tmp_path)
    monkeypatch.setattr(pilot, "RESULTS", tmp_path / "results" / pilot.STUDY)
    old = tmp_path / "results" / "old" / "trials.jsonl"
    old.parent.mkdir(parents=True)
    old.write_text(json.dumps({"seed": 5001}) + "\n")
    with pytest.raises(ValueError, match="overlaps"):
        pilot.check_seed_overlap(pilot.load_config())


def test_mock_run_cells_identity_and_no_overwrite(tmp_path):
    plan = pilot.make_plan(pilot.load_config())
    out = tmp_path / "mock"
    manifest = pilot.run(plan, out, "mock")
    rows = read_rows(out / "trials.jsonl")
    assert manifest["status"] == "mock_complete" and manifest["mock_only"]
    assert len(rows) == 24
    assert {(r["requested_model"], r["seed"], r["cond"], r["authorization"]) for r in rows} == {
        (m["id"], seed, cond, auth) for m in plan["config"]["models"]
        for seed in plan["config"]["seeds"] for cond in plan["config"]["conditions"]
        for auth in plan["config"]["authorizations"]}
    assert all(r["mock_only"] and r["backend"] == "adaption-mock" and
               r["model"] == "scripted-mock:" + r["requested_model"] and
               r["run_id"] == manifest["run_id"] and r["protocol_hash"] == manifest["protocol_hash"]
               for r in rows)
    analyze.validate_rows(rows, analyze.DEFAULT_BY)
    with pytest.raises(ValueError, match="merge"):
        analyze.validate_rows(rows, ("cond",))
    before = (out / "trials.jsonl").read_bytes()
    with pytest.raises(ValueError, match="exists"):
        pilot.run(plan, out, "mock")
    assert (out / "trials.jsonl").read_bytes() == before


@pytest.mark.parametrize("approval", [None, "wrong"])
def test_bad_approval_never_reads_key_or_constructs_backend(tmp_path, monkeypatch, approval):
    plan = pilot.make_plan(pilot.load_config())
    monkeypatch.setattr(pilot, "preflight_models", lambda *_: pytest.fail("preflight before approval"))
    monkeypatch.setattr(backend, "Adaption", lambda *a, **k: pytest.fail("backend before approval"))
    monkeypatch.setattr(pilot.os.environ, "get", lambda *a, **k: pytest.fail("environment read before approval"))
    out = tmp_path / "live"
    with pytest.raises(ValueError, match="approve-plan"):
        pilot.run(plan, out, "execute", approval)
    assert not out.exists()


def test_config_and_source_drift_invalidates_approval(tmp_path, monkeypatch):
    config = pilot.load_config()
    plan = pilot.make_plan(config)
    changed = copy.deepcopy(plan)
    changed["config"]["schedule_seed"] += 1
    with pytest.raises(ValueError, match="stale"):
        pilot.run(changed, tmp_path / "config", "execute", plan["approval_sha256"])
    for name in pilot.SOURCE_FILES:
        (tmp_path / name).write_bytes((pilot.HERE / name).read_bytes())
    monkeypatch.setattr(pilot, "HERE", tmp_path)
    (tmp_path / pilot.SOURCE_FILES[0]).write_text("source changed")
    with pytest.raises(ValueError, match="stale"):
        pilot.run(plan, tmp_path / "source", "execute", plan["approval_sha256"])


def test_output_guard_protects_frozen_results():
    with pytest.raises(ValueError, match="in-repo outputs"):
        pilot.safe_output(pilot.HERE / "results" / "v2" / "new")
    assert pilot.safe_output(pilot.RESULTS / "new") == (pilot.RESULTS / "new").resolve()
    with pytest.raises(ValueError):
        pilot.safe_output(pilot.RESULTS)


def test_approved_execute_with_fake_api_preserves_audit_and_identity(tmp_path, monkeypatch):
    config = pilot.load_config()
    config["seeds"] = [5000]
    plan = pilot.make_plan(config)
    monkeypatch.setattr(pilot, "preflight_models", lambda cfg: sorted(m["id"] for m in cfg["models"]))
    monkeypatch.setenv("ADAPTION_API_KEY", "local-fake-key")
    sent = []

    class Response:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(self.data).encode()

    def fake_urlopen(request, timeout):
        payload = json.loads(request.data)
        sent.append(payload)
        response = Response()
        response.data = {"id": f"response-{len(sent)}", "model": payload["model"], "status": "completed", "error": None,
                         "incomplete_details": None, "usage": {"input_tokens": 100, "output_tokens": 2},
                         "output": [{"type": "message", "role": "assistant", "content": [
                             {"type": "output_text", "text": "PASS"}]}]}
        return response

    monkeypatch.setattr(backend.urllib.request, "urlopen", fake_urlopen)
    out = tmp_path / "live"
    manifest = pilot.run(plan, out, "execute", plan["approval_sha256"])
    rows = read_rows(out / "trials.jsonl")
    assert manifest["status"] == "complete" and not manifest["mock_only"]
    assert len(rows) == 8 and len(sent) == 40
    for row in rows:
        assert row["backend"] == "adaption" and row["model"] == row["requested_model"]
        assert row["run_id"] == manifest["run_id"] and not row["mock_only"]
        for turn in row["turns"]:
            record = turn["adaption"]
            assert record["request"]["model"] == row["requested_model"] == record["model"]
            assert record["sent"] and record["raw"]["status"] == "completed"
            assert record["usage"] == {"input_tokens": 100, "output_tokens": 2}
    events = read_rows(out / "calls.jsonl")
    assert len(events) == 80
    attempts = {e["call_id"]: e for e in events if e["event"] == "attempt"}
    results = {e["call_id"]: e for e in events if e["event"] == "result"}
    assert len(attempts) == len(results) == 40 and attempts.keys() == results.keys()
    response_ids = set()
    for row in rows:
        for turn in row["turns"]:
            record = turn["adaption"]
            response_ids.add(record["raw"]["id"])
            attempt, result = attempts[record["call_id"]], results[record["call_id"]]
            assert result["record"] == record
            assert attempt["requested_model"] == row["requested_model"]
            assert (attempt["seed"], attempt["cond"], attempt["authorization"]) == (row["seed"], row["cond"], row["authorization"])
            assert attempt["run_id"] == row["run_id"] and result["trial_id"] == attempt["trial_id"]
    assert len(response_ids) == 40
    analyze.validate_rows(rows, analyze.DEFAULT_BY)
    mock_out = tmp_path / "mock"
    pilot.run(plan, mock_out, "mock")
    both = rows + read_rows(mock_out / "trials.jsonl")
    analyze.validate_rows(both, analyze.DEFAULT_BY)
    with pytest.raises(ValueError, match="merge"):
        analyze.validate_rows(both, ("model", "cond"))


@pytest.mark.parametrize("attribute", ["PILOT_PROTOCOL", "source"])
def test_protocol_document_drift_invalidates_approval(tmp_path, monkeypatch, attribute):
    plan = pilot.make_plan(pilot.load_config())
    doc = tmp_path / "protocol.md"
    original = pilot.PILOT_PROTOCOL if attribute == "PILOT_PROTOCOL" else pilot.p.PROTOCOL
    doc.write_bytes(original.read_bytes() + b"\nChanged protocol.\n")
    monkeypatch.setattr(pilot if attribute == "PILOT_PROTOCOL" else pilot.p,
                        "PILOT_PROTOCOL" if attribute == "PILOT_PROTOCOL" else "PROTOCOL", doc)
    monkeypatch.setattr(pilot, "preflight_models", lambda *_: pytest.fail("preflight on stale plan"))
    with pytest.raises(ValueError, match="stale"):
        pilot.run(plan, tmp_path / "run", "execute", plan["approval_sha256"])


def prepare_fake_run(monkeypatch):
    config = pilot.load_config()
    config["seeds"] = [5000]
    plan = pilot.make_plan(config)
    monkeypatch.setattr(pilot, "preflight_models", lambda cfg: [m["id"] for m in cfg["models"]])
    monkeypatch.setenv("ADAPTION_API_KEY", "local-fake-key")
    return config, plan


class FakeResponse:
    status = 200
    def __init__(self, payload, usage=None):
        self.data = {"id": "response-" + payload["model"], "model": payload["model"],
                     "status": "completed", "error": None, "incomplete_details": None,
                     "usage": usage, "output": [{"type": "message", "role": "assistant",
                       "content": [{"type": "output_text", "text": "PASS"}]}]}
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return json.dumps(self.data).encode()


def test_interrupted_request_keeps_previous_result_and_aborted_manifest(tmp_path, monkeypatch):
    _, plan = prepare_fake_run(monkeypatch)
    sent = []
    def fake_urlopen(request, timeout):
        sent.append(json.loads(request.data))
        if len(sent) == 2:
            raise KeyboardInterrupt()
        return FakeResponse(sent[-1], {"input_tokens": 100, "output_tokens": 2})
    monkeypatch.setattr(backend.urllib.request, "urlopen", fake_urlopen)
    out = tmp_path / "interrupted"
    with pytest.raises(KeyboardInterrupt):
        pilot.run(plan, out, "execute", plan["approval_sha256"])
    events = read_rows(out / "calls.jsonl")
    assert [e["event"] for e in events] == ["attempt", "result", "attempt"]
    assert events[0]["call_id"] == events[1]["call_id"] != events[2]["call_id"]
    assert events[1]["record"]["raw"]["id"].startswith("response-")
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["status"] == "aborted: KeyboardInterrupt" and manifest["totals"]["rows"] == 0


def test_missing_usage_stops_before_any_further_posts(tmp_path, monkeypatch):
    _, plan = prepare_fake_run(monkeypatch)
    sent = []
    def fake_urlopen(request, timeout):
        sent.append(json.loads(request.data))
        return FakeResponse(sent[-1])
    monkeypatch.setattr(backend.urllib.request, "urlopen", fake_urlopen)
    out = tmp_path / "missing-usage"
    manifest = pilot.run(plan, out, "execute", plan["approval_sha256"])
    assert len(sent) == 1 and manifest["status"].startswith("stopped:")
    events = read_rows(out / "calls.jsonl")
    assert sum(e["event"] == "attempt" for e in events) == 1
    assert next(e for e in events if e["event"] == "result")["record"]["failure"] == "missing_or_invalid_usage"


def test_credit_limit_is_shared_across_models(tmp_path, monkeypatch):
    config, plan = prepare_fake_run(monkeypatch)
    a, b = config["models"]
    monkeypatch.setattr(pilot, "jobs", lambda cfg: [(a, 5000, "local", "authorized"),
                                                   (b, 5000, "local", "authorized")])
    sent = []
    def fake_urlopen(request, timeout):
        payload = json.loads(request.data)
        sent.append(payload)
        usage = {"input_tokens": 2_760_000 if len(sent) == 5 else 100, "output_tokens": 0}
        return FakeResponse(payload, usage)
    monkeypatch.setattr(backend.urllib.request, "urlopen", fake_urlopen)
    out = tmp_path / "shared-budget"
    manifest = pilot.run(plan, out, "execute", plan["approval_sha256"])
    assert len(sent) == 5 and {r["model"] for r in sent} == {a["id"]}
    assert manifest["status"].startswith("stopped:")
    events = read_rows(out / "calls.jsonl")
    assert any(e["event"] == "result" and e["requested_model"] == b["id"] and
               e["record"]["failure"] == "credit_budget" for e in events)
