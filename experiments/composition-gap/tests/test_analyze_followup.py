import json, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analyze_followup.py"


@pytest.fixture
def af(tmp_path):
    """Helper half of analyze_followup.py (everything before the import-time analysis), pointed at tmp_path."""
    sys.path.insert(0, str(ROOT))
    ns = {"__file__": str(SCRIPT), "__name__": "af"}
    exec(compile(SCRIPT.read_text().split("# --- analysis (runs on import) ---")[0], str(SCRIPT), "exec"), ns)
    ns["BASE"] = tmp_path
    (tmp_path / "results").mkdir()
    return ns


def row(seed=1, **kw):
    r = {"run_id": "r1", "design": "v2", "backend": "claude-code", "model": "m", "policy": "none",
         "framing": "neutral", "cond": "solo", "seed": seed, "failed_calls": 0}
    r.update(kw)
    return r


def write(tmp_path, name, rows):
    (tmp_path / "results" / name).write_text("".join(json.dumps(r) + "\n" for r in rows))


def test_duplicate_trial_raises(af, tmp_path):
    write(tmp_path, "a.jsonl", [row(1), row(1)])
    with pytest.raises(ValueError, match="duplicate trial"):
        af["load"](["results/*.jsonl"], model="m", framings=("neutral",))


def test_duplicate_trial_across_runs_raises(af, tmp_path):
    write(tmp_path, "a.jsonl", [row(1)])
    write(tmp_path, "b.jsonl", [row(1, run_id="r2")])
    with pytest.raises(ValueError, match="duplicate trial"):
        af["load"](["results/*.jsonl"], model="m", framings=("neutral",))


def test_mixed_model_raises(af, tmp_path):
    write(tmp_path, "a.jsonl", [row(1), row(2, model="other")])
    with pytest.raises(ValueError, match="unexpected model"):
        af["load"](["results/*.jsonl"], model="m", framings=("neutral",))


def test_empty_glob_raises(af):
    with pytest.raises(FileNotFoundError, match="no result files match"):
        af["load"](["results/nothing_*.jsonl"], model="m", framings=("neutral",))


def test_clean_load_passes_and_missing_failed_calls_is_not_valid(af, tmp_path):
    missing = row(2)
    del missing["failed_calls"]
    write(tmp_path, "a.jsonl", [row(1), missing, row(3, failed_calls=2)])
    rows = af["load"](["results/*.jsonl"], model="m", framings=("neutral",))
    assert [r["seed"] for r in rows if r.get("failed_calls") == 0] == [1]
