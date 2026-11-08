"""The published evidence must audit from a relocated checkout without inference."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import urllib.request

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import adaption_pilot as pilot
import audit_adaption_pilot as audit


@pytest.fixture
def published(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("offline audit attempted a network request")
    monkeypatch.setattr(urllib.request, "urlopen", no_network)
    monkeypatch.delenv("ADAPTION_API_KEY", raising=False)
    destination = tmp_path / "relocated-evidence"
    shutil.copytree(pilot.RESULTS, destination)
    return destination


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def test_published_evidence_audits_after_relocation(published):
    before = hashes(published)
    result = audit.audit(published)
    assert result["status"] == "offline_audit_passed"
    assert (result["assigned_trials"], result["valid_trials"], result["failed_trials"]) == (24, 21, 3)
    assert result["successful_source_calls_not_resent"] == 27
    assert result["cumulative_actual_post_attempts"] == 117
    assert result["cumulative_accounted_credits"] == pytest.approx(0.28227638)
    assert hashes(published) == before


@pytest.mark.parametrize("target", ["source", "combined", "summary", "usage", "hashset"])
def test_published_evidence_changes_fail_closed(published, target):
    continuation = published / "pilot-03-resume"
    if target in ("summary", "usage", "hashset"):
        path = continuation / "summary.json"
        value = json.loads(path.read_text())
        if target == "summary":
            value["cumulative_accounted_credits"] = 0
        elif target == "usage":
            value["models"]["qwen3.5-397b"]["input_tokens"] += 1
        else:
            value["artifact_sha256"] = {}
        path.write_text(json.dumps(value))
    else:
        path = (published / "pilot-02" / "calls.jsonl" if target == "source"
                else continuation / "combined_trials.jsonl")
        path.write_bytes(path.read_bytes() + b"\n")
    before = hashes(published)
    with pytest.raises(ValueError, match="differs"):
        audit.audit(published)
    assert hashes(published) == before
