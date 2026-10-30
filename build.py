#!/usr/bin/env python3
"""Build the Free School Year Organizer Kit.

Renders every HTML sheet in src/ to an unbranded, print-ready PDF in
printables/ using WeasyPrint. No network access, no signups, no tracking.

Usage:
    python3 build.py                 # build all sheets (plus verification by default)
    python3 build.py --out /tmp/x    # write PDFs somewhere other than printables/
    python3 build.py --skip-verify   # build only, skip PDF sanity checks

Requirements: WeasyPrint (pip install weasyprint). Verified with WeasyPrint 70.
"""

import argparse
import io
import pathlib
import sys

try:
    from weasyprint import HTML
except ImportError as exc:
    sys.stderr.write(
        "WeasyPrint is required to build this kit.\n"
        "Install it with:  pip install weasyprint\n"
        f"(Details: {exc})\n"
    )
    sys.exit(1)


def _make_fonts_deterministic():
    """Pin subset-font dates so repeated builds produce identical PDFs.

    WeasyPrint subsets embedded fonts via HarfBuzz or fontTools, and both can
    stamp the current time (or reorder tables) into the font's `head` on each
    run. We therefore force the fontTools path and recompile each subset font
    with a fixed date and checksum. Glyphs, text, and layout are untouched,
    but repeated builds produce byte-identical PDFs.
    """
    from fontTools.ttLib import TTFont

    import weasyprint.pdf.fonts as wpfonts

    wpfonts.harfbuzz_subset = None

    # Seconds since the 1904 Mac epoch for 2026-01-01 00:00:00 UTC.
    fixed_int = 2082844800 + 1767225600
    original_clean = wpfonts.Font.clean

    def clean_and_pin(self, to_unicode, hinting):
        """Run clean(), then pin dates. clean() may re-save the font after
        subsetting (variable-font instantiation), so this must be the last
        font-touching step to truly be deterministic."""
        original_clean(self, to_unicode, hinting)
        font = TTFont(io.BytesIO(self.file_content), fontNumber=self.index)
        head = font["head"]
        head.created = fixed_int
        head.modified = fixed_int
        font.recalcTimestamp = False
        buffer = io.BytesIO()
        font.save(buffer)
        self.file_content = buffer.getvalue()

    wpfonts.Font.clean = clean_and_pin

ROOT = pathlib.Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
OUT_DIR = ROOT / "printables"

def build_sheet(html_path: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path:
    """Render one HTML sheet to a PDF file and return the output path."""
    pdf_path = out_dir / (html_path.stem + ".pdf")
    HTML(filename=str(html_path), base_url=str(html_path.parent)).write_pdf(
        str(pdf_path)
    )
    return pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build printable PDFs from the HTML sheets in src/."
    )
    parser.add_argument(
        "--out",
        default=str(OUT_DIR),
        help="directory to write the PDFs into (default: printables/)",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="build the PDFs but skip the quick sanity checks",
    )
    args = parser.parse_args()
    out_dir = pathlib.Path(args.out)
    _make_fonts_deterministic()

    if not out_dir.exists():
        out_dir.mkdir(parents=True)

    sheets = sorted(SRC_DIR.glob("[0-9]*.html"))
    if not sheets:
        sys.stderr.write(f"No numbered HTML sheets found in {SRC_DIR}\n")
        return 1

    built = 0
    failed = 0
    for sheet in sheets:
        try:
            pdf = build_sheet(sheet, out_dir)
            size_kb = pdf.stat().st_size / 1024
            print(f"  built {pdf.name}  ({size_kb:.0f} KB)")
            built += 1
        except Exception as exc:  # noqa: BLE001 - report every failure to the user
            sys.stderr.write(f"  FAILED {sheet.name}: {exc}\n")
            failed += 1

    if failed:
        sys.stderr.write(
            f"{failed} sheet(s) failed to build; {built} succeeded. "
            "See messages above.\n"
        )
        return 1

    if not args.skip_verify:
        sys.path.insert(0, str(ROOT / "tests"))
        try:
            import verify_pdfs
        except ImportError:
            sys.stderr.write(
                "Could not load tests/verify_pdfs.py; skipping verification.\n"
            )
            return 0
        problems = verify_pdfs.check_built(out_dir, SRC_DIR)
        if problems:
            for problem in problems:
                sys.stderr.write(f"  VERIFY FAILED: {problem}\n")
            sys.stderr.write("Verification failed.\n")
            return 1
        print(f"  verified: all {built} PDFs are valid ({built}/{built} passed)")

    print(f"Done. {built} unbranded PDF(s) in {out_dir} - print on Letter, enjoy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
