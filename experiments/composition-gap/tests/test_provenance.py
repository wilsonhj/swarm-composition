"""Offline study tests: information boundaries, publication gates, and provenance."""
import json

import pytest

import harness as h
import provenance as p
from scoring import score_row


@pytest.mark.parametrize("condition", p.CONDITIONS)
@pytest.mark.parametrize("authorization", p.OBJECTIVES)
def test_scripted_positive_and_negative_paths(condition, authorization):
    r = p.run_trial(p.StudyMock(), 2000, condition, authorization)
    expected = authorization == "authorized" or condition == "local"
    assert r["recoverable"] == r["assembled"] == expected
    assert r["actor_calls"] == 5 and r["failed_calls"] == 0
    assert r["monitor_calls"] == (5 if condition == "monitor" and expected else
                                   4 if condition == "monitor" else 0)
    assert r["authorized_completed"] == (authorization == "authorized")


def test_local_prompts_cannot_distinguish_authorization():
    def capture(authorization):
        seen = []
        def llm(system, user): seen.append((system, user)); return "PASS"
        p.run_trial(llm, 2000, "local", authorization)
        return seen
    assert capture("authorized") == capture("restricted")


def test_shared_provenance_changes_only_system_metadata():
    seen = []
    def llm(system, user): seen.append((system, user)); return "PASS"
    p.run_trial(llm, 2000, "provenance", "restricted")
    assert len(seen) == 5
    assert all(system == p.ACTOR + p.PROVENANCE.format(objective=p.OBJECTIVES["restricted"])
               for system, _ in seen)
    assert all(p.OBJECTIVES["restricted"] not in user for _, user in seen)


def test_blocked_candidates_remain_private_to_scoring_and_assembler():
    _, words, _ = h.make_task(2000)
    candidates = iter(words)
    seen_monitor, seen_assembler = [], []
    def llm(system, user):
        if system == p.MONITOR:
            seen_monitor.append(json.loads(user))
            return "BLOCK"
        if user.startswith("Inventory list:"):
            return "POST: " + next(candidates)
        seen_assembler.append(user)
        return "PASS"
    r = p.run_trial(llm, 2000, "monitor", "restricted")
    assert r["board"] == [] and score_row(r)["identified_parts"] == 0
    assert r["blocked_posts"] == 4 and all(x["accepted_board"] == [] for x in seen_monitor)
    assert all("seed" not in x and "secret" not in x and "lists" not in x for x in seen_monitor)
    assert all(not any(w in prompt for w in words) for prompt in seen_assembler)
    assert len([t for t in r["turns"] if t.get("proposed")]) == 4


@pytest.mark.parametrize("verdict", ["PASS", "ALLOW plus explanation", "POST: ALLOW"])
def test_invalid_monitor_verdict_fails_closed_and_invalidates_trial(verdict):
    _, words, _ = h.make_task(2000)
    def llm(system, user): return verdict if system == p.MONITOR else "POST: " + words[0]
    r = p.run_trial(llm, 2000, "monitor", "restricted")
    assert r["board"] == [] and not r["valid"] and r["protocol_errors"] == 5


def test_backend_monitor_failure_is_recorded_once():
    class FailedMonitor(p.StudyMock):
        def __call__(self, system, user):
            return self._fail() if system == p.MONITOR else super().__call__(system, user)
    r = p.run_trial(FailedMonitor(), 2000, "monitor", "restricted")
    assert r["board"] == [] and r["failed_calls"] == 4 and r["protocol_errors"] == 0


def test_malformed_actor_post_does_not_enter_board():
    r = p.run_trial(lambda *_: "POSTER: not a valid post", 2000, "local", "authorized")
    assert r["board"] == [] and r["protocol_errors"] == 5 and not r["valid"]


@pytest.mark.parametrize("git", [{"commit": "a" * 40, "dirty": True},
                                 {"commit": "b" * 40, "dirty": False}])
def test_heldout_requires_matching_clean_freeze_before_model_calls(tmp_path, monkeypatch, git):
    monkeypatch.setattr(h, "git_info", lambda: git)
    def forbidden(*a, **kw): pytest.fail("backend must not be created for an invalid freeze")
    monkeypatch.setattr(h, "ClaudeCode", forbidden)
    with pytest.raises(SystemExit):
        p.main(["--backend", "claude-code", "--phase", "heldout", "--seeds", "50", "--seed-offset", "3000",
                "--freeze-commit", "a" * 40, "--out", str(tmp_path / "x.jsonl")])


def test_cli_mock_writes_unique_provenance_and_all_six_cells(tmp_path):
    out = tmp_path / "nested" / "smoke.jsonl"
    p.main(["--seeds", "2", "--out", str(out)])
    rows = [json.loads(s) for s in out.read_text().splitlines()]
    m = json.loads((out.parent / "smoke.jsonl.manifest.json").read_text())
    assert len(rows) == 12 and m["status"] == "complete" and m["totals"]["failed_rows"] == 0
    assert {(r["cond"], r["authorization"]) for r in rows} == {
        (c, a) for c in p.CONDITIONS for a in p.OBJECTIVES}
    assert all(r["protocol_hash"] == m["protocol_hash"] and r["prompt_hash"] == m["prompt_hash"]
               and r["run_id"] == m["run_id"] and r["model"] == "scripted-study-mock" for r in rows)
    with pytest.raises(SystemExit): p.main(["--out", str(out)])
    assert len(out.read_text().splitlines()) == 12


@pytest.mark.parametrize("args", [["--phase", "heldout"], ["--seed-offset", "3000"],
                                   ["--seeds", "0"], ["--workers", "0"]])
def test_cli_rejects_invalid_or_unfrozen_run_before_backend(tmp_path, args):
    out = tmp_path / "x.jsonl"
    with pytest.raises(SystemExit): p.main([*args, "--out", str(out)])
    assert not out.exists()


# ---------------------------------------------------------------- runner review: usage errors, no stray dirs

@pytest.fixture
def no_dotenv(monkeypatch):
    monkeypatch.setattr(h, "load_env", lambda path=None: None)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-not-a-key")


@pytest.mark.parametrize("args", [["--model", "a/b"], ["--model", "plain", "--max-usd", "1"]])
def test_openrouter_needs_slug_and_explicit_budget_and_leaves_no_dirs(tmp_path, monkeypatch, no_dotenv, args):
    monkeypatch.setenv("OPENROUTER_BUDGET_USD", "5")  # the protocol requires an explicit --max-usd
    def forbidden(*a, **kw): pytest.fail("OpenRouter must not be created for a rejected invocation")
    monkeypatch.setattr(h, "OpenRouter", forbidden)
    with pytest.raises(SystemExit) as e:
        p.main(["--backend", "openrouter", *args, "--out", str(tmp_path / "new" / "x.jsonl")])
    assert e.value.code == 2 and not (tmp_path / "new").exists()


@pytest.mark.parametrize("budget", ["0", "-1", "nan", "inf"])
def test_openrouter_invalid_budget_is_usage_error(tmp_path, no_dotenv, capsys, budget):
    with pytest.raises(SystemExit) as e:
        p.main(["--backend", "openrouter", "--model", "a/b", "--max-usd", budget,
                "--out", str(tmp_path / "new" / "x.jsonl")])
    assert e.value.code == 2 and "usage:" in capsys.readouterr().err and not (tmp_path / "new").exists()


@pytest.mark.parametrize("args", [["--phase", "heldout"], ["--seed-offset", "3000"], ["--seeds", "0"]])
def test_rejected_invocation_creates_no_output_dir(tmp_path, args):
    with pytest.raises(SystemExit): p.main([*args, "--out", str(tmp_path / "new" / "x.jsonl")])
    assert not (tmp_path / "new").exists()


def test_existing_output_rejected_before_backend(tmp_path, monkeypatch):
    out = tmp_path / "x.jsonl"
    out.write_text("")
    def forbidden(*a, **kw): pytest.fail("backend must not be created when the output exists")
    monkeypatch.setattr(p, "StudyMock", forbidden)
    with pytest.raises(SystemExit): p.main(["--out", str(out)])
