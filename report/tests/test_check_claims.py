"""Mutation checks for document values and the generated claim ledger (offline)."""
import contextlib
import csv
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CLAIM_IDS = {"WD26", "WD36", "WD52", "WD65", "WD68", "WB19", "WB24"}


class CheckClaimsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="check-claims-test-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.repo = Path(cls.temp.name) / "repo"
        subprocess.run(["git", "clone", "--quiet", "--shared", str(ROOT), str(cls.repo)], check=True)
        # Exercise the current checker, including uncommitted fixes, against real
        # frozen inputs and git history without changing the source checkout.
        shutil.copyfile(ROOT / "report/tools/check_claims.py", cls.repo / "report/tools/check_claims.py")
        spec = importlib.util.spec_from_file_location("claim_checker_under_test",
                                                    cls.repo / "report/tools/check_claims.py")
        cls.checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.checker)
        cls.checker.CLAIMS = [c for c in cls.checker.CLAIMS if c["cid"] in CLAIM_IDS]

    def setUp(self):
        self.draft = self.repo / "report/draft.md"
        self.draft.write_text((ROOT / "report/draft.md").read_text())
        with (ROOT / "report/claim-ledger.csv").open() as source:
            self.rows = [r for r in csv.DictReader(source) if r["claim_id"] in CLAIM_IDS]
        self.write_ledger()

    def write_ledger(self):
        with self.checker.LEDGER.open("w") as target:
            writer = csv.DictWriter(target, fieldnames=self.checker.COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows)

    def check(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = self.checker.main(["--quiet"])
        return result, output.getvalue()

    def test_unchanged_document_and_ledger_pass(self):
        result, output = self.check()
        self.assertEqual(result, 0, output)

    def test_numeric_table_changes_fail_without_changing_row_labels(self):
        original = self.draft.read_text()
        for before, after in (
            ("| solo | 19/20 |", "| solo | 99/20 |"),
            ("| pipeline | 2/20 |", "| pipeline | 9/20 |"),
            ("47/49 / **33/49**", "47/49 / **3/49**"),
        ):
            with self.subTest(change=after):
                self.assertIn(before, original)
                self.draft.write_text(original.replace(before, after, 1))
                result, output = self.check()
                self.assertEqual(result, 2, output)

    def test_number_outside_needle_on_cited_line_fails(self):
        original = self.draft.read_text()
        needle = next(c for c in self.checker.CLAIMS if c["cid"] == "WD52")["needle"]
        for before, after in (("rerun, +10 pp [0, +30]", "rerun, +90 pp [0, +30]"),
                              ("Sonnet refused 20 of 20", "Sonnet refused 12 of 20")):
            with self.subTest(change=after):
                self.assertIn(before, original)
                self.assertNotIn(before, needle)
                self.draft.write_text(original.replace(before, after, 1))
                result, output = self.check()
                self.assertEqual(result, 2, output)
                self.assertIn("WD52: ledger line_numbers=", output)

    def test_value_as_written_differing_from_recompute_is_a_mismatch(self):
        spec = next(c for c in self.checker.CLAIMS if c["cid"] == "WD26")
        original = spec["written"]
        self.addCleanup(spec.__setitem__, "written", original)
        spec["written"] = original.replace("19/20", "18/20", 1)
        self.assertNotEqual(spec["written"], original)
        self.rows = self.checker.build_all()  # ledger consistent with specs, so only the mismatch remains
        self.write_ledger()
        result, output = self.check()
        self.assertEqual(result, 1, output)
        self.assertIn("MISMATCHES", output)
        self.assertIn("WD26", output)

    def test_ledger_estimates_denominators_and_provenance_must_match(self):
        row = next(r for r in self.rows if r["claim_id"] == "WD68")
        for field, changed in (
            ("estimate", "0pp"),
            ("collection_commit", "deadbee"),
            ("analysis_commit", "deadbee"),
            ("protocol_sha256", "0" * 64),
            ("run_ids", "wrong-run"),
            ("n_valid", "999"),
            ("interval", "[0, 0]"),
        ):
            with self.subTest(field=field):
                original = row[field]
                self.assertNotEqual(original, changed)
                row[field] = changed
                self.write_ledger()
                result, output = self.check()
                self.assertEqual(result, 2, output)
                row[field] = original

    def test_duplicate_row_replacing_a_cell_fails_table_audit(self):
        appb = self.repo / "report/appendix-b.md"
        original = appb.read_text()
        self.addCleanup(appb.write_text, original)
        lines = original.splitlines(keepends=True)
        first = next(i for i, ln in enumerate(lines) if ln.startswith("| claude-haiku-5-5 | none | explicit | pipeline |"))
        self.assertTrue(lines[first + 1].startswith("| claude-haiku-5-5 | none | explicit | relay_informed |"))
        lines[first + 1] = lines[first]
        appb.write_text("".join(lines))
        spec = next(c for c in self.checker_full().CLAIMS if c["cid"] == "WB03")
        value = spec["fn"]().value
        self.assertNotEqual(value, "32/32 rows identical")
        self.assertIn("duplicate rows", value)
        self.assertIn("none/explicit/relay_informed", value)

    def test_historical_documents_load_without_git_history(self):
        checker = self.checker_full()
        with tempfile.TemporaryDirectory() as bare:
            shutil.copytree(ROOT / checker.HISTORY_DIR, Path(bare) / checker.HISTORY_DIR)
            checker.ROOT = Path(bare)  # no .git: f1c1387 cannot be resolved
            for doc in checker.HISTORY_SHA256:
                self.assertIsNotNone(checker.doc_text(doc, checker.HEAD_PASS), doc)
            tampered = Path(bare) / checker.HISTORY_DIR / "report/draft.md"
            tampered.write_text(tampered.read_text() + "x")
            self.assertIsNone(checker.doc_text("report/draft.md", checker.HEAD_PASS))

    def test_duplicate_run_replacing_another_fails_claim_check(self):
        appb = self.repo / "report/appendix-b.md"
        original = appb.read_text()
        self.addCleanup(appb.write_text, original)
        lines = original.splitlines(keepends=True)
        first = next(i for i, ln in enumerate(lines) if ln.startswith("| 55325c9a | none / explicit |"))
        self.assertTrue(lines[first + 1].startswith("| 55325c9a | none / neutral |"))
        lines[first + 1] = lines[first]
        appb.write_text("".join(lines))
        result, output = self.check()
        self.assertEqual(result, 2, output)
        self.assertIn("WB19", output)
        self.assertIn("duplicate rows", output)
        self.assertIn("missing:", output)

    def test_duplicate_field_replacing_call_count_fails_claim_check(self):
        appb = self.repo / "report/appendix-b.md"
        original = appb.read_text()
        self.addCleanup(appb.write_text, original)
        lines = original.splitlines(keepends=True)
        first = next(i for i, ln in enumerate(lines) if ln.startswith("| status |"))
        self.assertTrue(lines[first + 1].startswith("| manifest `totals.calls` |"))
        lines[first + 1] = lines[first]
        appb.write_text("".join(lines))
        result, output = self.check()
        self.assertEqual(result, 2, output)
        self.assertIn("WB24", output)
        self.assertIn("duplicate rows", output)
        self.assertIn("missing:", output)

    def checker_full(self):
        spec = importlib.util.spec_from_file_location("claim_checker_full", self.repo / "report/tools/check_claims.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


if __name__ == "__main__":
    unittest.main()
