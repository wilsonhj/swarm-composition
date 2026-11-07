"""End-to-end and negative-path tests for tools/replay_provenance.py.

Run from the repository root (needs git history containing the pinned commits; no network):
    python -m unittest discover -s docs/handoffs/tests -v
Each test replays a private `git clone --shared` of the pinned snapshot, so the
source checkout and its worktree list are not modified.
"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HANDOFFS = pathlib.Path(__file__).resolve().parents[1]
TOOL = HANDOFFS / "tools" / "replay_provenance.py"
CONTRACT = json.loads((HANDOFFS / "provenance-inputs.json").read_text())
RAW = next(f["path"] for f in CONTRACT["files"] if f["kind"] == "raw")
# Runs the tool's own CLI with a substituted input contract.
WRAPPER = ("import importlib.util, pathlib, sys; "
           "spec = importlib.util.spec_from_file_location('replay_provenance', sys.argv[1]); "
           "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
           "m.CONTRACT_PATH = pathlib.Path(sys.argv[2]); sys.argv = [sys.argv[1], *sys.argv[3:]]; m.cli()")


class ReplayProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="replay-provenance-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "snapshot"
        source = subprocess.check_output(["git", "-C", str(HANDOFFS), "rev-parse", "--show-toplevel"],
                                         text=True).strip()
        subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", source, str(self.repo)],
                       check=True)
        subprocess.run(["git", "-C", str(self.repo), "checkout", "--quiet", "--detach",
                        CONTRACT["source_snapshot"]], check=True)
        self.out = self.tmp / "out" / "replay"

    def run_tool(self, contract=None):
        args = ["--repo", str(self.repo), "--out", str(self.out)]
        if contract is None:
            cmd = [sys.executable, str(TOOL), *args]
        else:
            path = self.tmp / "contract.json"
            path.write_text(json.dumps(contract))
            cmd = [sys.executable, "-c", WRAPPER, str(TOOL), str(path), *args]
        return subprocess.run(cmd, capture_output=True, text=True)

    def assert_failed_cleanly(self, result, message):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertFalse(self.out.exists())
        if self.out.parent.exists():
            self.assertEqual(list(self.out.parent.iterdir()), [], "partial output left behind")

    def test_canonical_replay_passes(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: 800 trials in 16 cells; 4795 logged turns", result.stdout)
        audit = json.loads((self.out / "audit.json").read_text())
        self.assertEqual(audit["status"], "provenance_replay_passed")
        for line in (self.out / "SHA256SUMS").read_text().splitlines():
            digest, name = line.split("  ")
            self.assertEqual(hashlib.sha256((self.out / name).read_bytes()).hexdigest(), digest)

    def test_existing_output_refused(self):
        self.out.mkdir(parents=True)
        result = self.run_tool()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Refusing to overwrite output", result.stderr)

    def test_output_inside_checkout_refused(self):
        self.out = self.repo / "replay-out"
        result = self.run_tool()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Output must be outside the source checkout", result.stderr)

    def test_modified_input_fails_hash_check(self):
        with open(self.repo / RAW, "a") as f:
            f.write("\n")  # score-neutral change
        self.assert_failed_cleanly(self.run_tool(), "SHA256 mismatch")

    def test_tampered_score_with_repinned_hash_fails(self):
        raw = self.repo / RAW
        lines = raw.read_text().splitlines(keepends=True)
        row = json.loads(lines[0])
        row["recoverable"] = not row["recoverable"]
        lines[0] = json.dumps(row) + "\n"
        raw.write_text("".join(lines))
        contract = json.loads(json.dumps(CONTRACT))
        next(f for f in contract["files"] if f["kind"] == "raw")["sha256"] = \
            hashlib.sha256(raw.read_bytes()).hexdigest()
        self.assert_failed_cleanly(self.run_tool(contract), "Rebuilt trial differs from stored row")

    def test_late_failure_leaves_no_output(self):
        contract = json.loads(json.dumps(CONTRACT))
        contract["expected_reports"]["analysis_snapshot.md"] = "0" * 64
        self.assert_failed_cleanly(self.run_tool(contract), "Report differs from pinned output")

    def test_changed_expected_value_fails(self):
        contract = json.loads(json.dumps(CONTRACT))
        contract["expected"]["logged_turns"] = 4794
        self.assert_failed_cleanly(self.run_tool(contract), "Logged turns 4795 != 4794")

    def test_untracked_module_beside_sources_not_imported(self):
        for name in ("random.py", "json.py", "scoring.py.bak"):
            (self.repo / "experiments/composition-gap" / name).write_text("raise SystemExit('shadowed')\n")
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
