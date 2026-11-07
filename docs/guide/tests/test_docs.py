"""Integrity regressions for the maintained diagram exports; no rendering needed."""
import importlib.util
import pathlib
import shutil
import tempfile
import unittest

GUIDE = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_docs", GUIDE / "tools/check_docs.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class DiagramIntegrity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="swarm-doc-test-")
        self.addCleanup(self.temporary.cleanup)
        self.guide = pathlib.Path(self.temporary.name)
        shutil.copyfile(GUIDE / "architecture.md", self.guide / "architecture.md")
        shutil.copytree(GUIDE / "diagrams", self.guide / "diagrams")

    def test_reviewed_exports_match(self):
        self.assertEqual(checks.check_diagrams(self.guide), [])

    def test_changed_source_requires_export_review(self):
        source = self.guide / "architecture.md"
        source.write_text(source.read_text().replace("harness.py<br/>", "changed.py<br/>", 1))
        self.assertTrue(any("Stale diagram export" in e for e in checks.check_diagrams(self.guide)))

    def test_changed_svg_requires_review(self):
        path = self.guide / "diagrams/01-study-dataflow.svg"
        path.write_bytes(path.read_bytes() + b"\n")
        self.assertTrue(any("Changed diagram export" in e for e in checks.check_diagrams(self.guide)))


if __name__ == "__main__":
    unittest.main()
