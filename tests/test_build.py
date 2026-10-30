"""Tests for the Free School Year Organizer Kit.

Run with:
    python3 tests/test_build.py          (plain unittest, no extra runner needed)
or
    python3 -m unittest discover tests

Covers:
  1. Every source sheet exists with a title and shares the print stylesheet.
  2. Building runs end-to-end and emits every expected PDF in a temp directory.
  3. Every built PDF is a valid, readable, unbranded document (via verify_pdfs).
"""

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
tests_dir = ROOT / "tests"
sys.path.insert(0, str(tests_dir))

import verify_pdfs  # noqa: E402


class TestSources(unittest.TestCase):
    def test_all_eight_sheets_present(self):
        for stem in verify_pdfs.EXPECTED_SHEETS:
            path = SRC_DIR / f"{stem}.html"
            self.assertTrue(path.exists(), f"missing source sheet: {path.name}")

    def test_each_sheet_has_title_and_shared_stylesheet(self):
        for stem in verify_pdfs.EXPECTED_SHEETS:
            html = (SRC_DIR / f"{stem}.html").read_text(encoding="utf-8")
            self.assertIn("<title>", html, f"{stem}: no <title>")
            self.assertIn('href="print.css"', html, f"{stem}: does not link print.css")

    def test_stylesheet_exists(self):
        self.assertTrue((SRC_DIR / "print.css").exists())

    def test_no_branding_in_sources(self):
        for html_path in SRC_DIR.glob("*.html"):
            text = html_path.read_text(encoding="utf-8").lower()
            for brand in ("asdale dynamics", "asdale"):
                self.assertNotIn(brand, text, f"{html_path.name}: contains branding")

    def test_no_external_http_links_in_sources(self):
        for html_path in SRC_DIR.glob("*.html"):
            text = html_path.read_text(encoding="utf-8")
            self.assertNotIn(
                "https://", text, f"{html_path.name}: contains an external link"
            )
            self.assertNotIn(
                'http://', text, f"{html_path.name}: contains an external link"
            )

    def test_each_sheet_has_a_parent_guide(self):
        for stem in verify_pdfs.EXPECTED_SHEETS:
            html = (SRC_DIR / f"{stem}.html").read_text(encoding="utf-8")
            self.assertIn(
                'class="guide', html, f"{stem}: no parent-guide box found"
            )


class TestBuild(unittest.TestCase):
    def test_build_script_runs_and_outputs_all_pdfs(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_build(tmp)
            self.assertEqual(result.returncode, 0, f"build failed:\n{result.stdout}\n{result.stderr}")
            for stem in verify_pdfs.EXPECTED_SHEETS:
                pdf = pathlib.Path(tmp) / f"{stem}.pdf"
                self.assertTrue(pdf.exists(), f"build did not produce {stem}.pdf")
                self.assertGreater(pdf.stat().st_size, 1000, f"{stem}.pdf suspiciously tiny")

    def test_built_pdfs_are_valid_and_unbranded(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_build(tmp)
            problems = []
            SRC = verify_pdfs.EXPECTED_SHEETS  # noqa: N806
            for stem in SRC:
                problems.extend(
                    verify_pdfs.check_pdf(pathlib.Path(tmp) / f"{stem}.pdf", SRC_DIR)
                )
            self.assertEqual(problems, [], "PDF verification reported problems")

    @staticmethod
    def run_build(out_dir: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(ROOT / "build.py"), "--out", out_dir, "--skip-verify"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )


class TestRepoHygiene(unittest.TestCase):
    def test_readme_and_license_exist(self):
        self.assertTrue((ROOT / "README.md").exists())
        self.assertTrue((ROOT / "LICENSE").exists())

    def test_license_copyright_line_is_exact(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        line = "Copyright (c) 2026 Asdale Dynamics, LLC"
        self.assertIn(line + "\n", text, "LICENSE must contain the exact copyright line")

    def test_readme_credits_owner(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", text)

    def test_no_secrets_in_repo(self):
        patterns = ("api_key", "apikey", "bearer ", "begin private key", "sk-")
        for path in ROOT.rglob("*"):
            # The checker's own patterns live in tests/ and build.py's help text;
            # scanning those files would only find the pattern definitions.
            if "tests" in path.parts or path.name == "build.py":
                continue
            if not path.is_file() or any(
                part in path.parts for part in (".git", "printables")
            ):
                continue
            if path.suffix in {".pdf", ".pyc"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            for pattern in patterns:
                self.assertNotIn(
                    pattern.lower().replace(" ", ""),
                    text,
                    f"{path.name}: possible secret-like string ({pattern})",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
