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
CLAIM_IDS = {"WD26", "WD36", "WD65", "WD68"}


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


if __name__ == "__main__":
    unittest.main()
