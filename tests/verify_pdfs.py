"""Shared PDF checks used by build.py --verify and by the test suite.

These run without WeasyPrint: they inspect the PDFs WeasyPrint already
produced, using the lightweight pypdf reader, so the checks stay fast and
deterministic.
"""

import pathlib
import re
from urllib.parse import unquote

from pypdf import PdfReader

# A brand string we deliberately keep OUT of the printed sheets. This keeps the
# check honest if the PDFs ever change.
BRAND_STRINGS = ("Asdale Dynamics", "ASDALE DYNAMICS")

# All eight sheets, by filename stem, in kit order.
EXPECTED_SHEETS = (
    "01-first-week-checklist",
    "02-teacher-contact-tracker",
    "03-backpack-folder-map",
    "04-permission-slip-log",
    "05-activities-fees-calendar",
    "06-lunch-balance-card",
    "07-sick-day-readiness",
    "08-binder-cleanout",
)


def check_built(out_dir: pathlib.Path, src_dir: pathlib.Path | None = None):
    """Verify every expected sheet exists and builds a valid, unbranded PDF.

    Returns a list of problem strings; empty list means all checks passed.
    """
    problems = []
    out_dir = pathlib.Path(out_dir)

    if not out_dir.exists():
        return [f"output directory missing: {out_dir}"]

    for stem in EXPECTED_SHEETS:
        pdf_path = out_dir / f"{stem}.pdf"
        if not pdf_path.exists():
            problems.append(f"{stem}: PDF missing from {out_dir}")
            continue
        problems.extend(check_pdf(pdf_path, src_dir))

    extra = sorted(p.name for p in out_dir.glob("*.pdf") if p.stem not in EXPECTED_SHEETS)
    if extra:
        problems.append(f"unexpected PDFs in {out_dir}: {', '.join(extra)}")

    return problems


def check_pdf(pdf_path: pathlib.Path, src_dir: pathlib.Path | None = None):
    """Run all checks for one PDF and return a list of problems (empty = ok)."""
    problems = []

    # 1. Starts with a PDF header (%PDF-n.n).
    with open(pdf_path, "rb") as fh:
        head = fh.read(16)
    if not head.startswith(b"%PDF-"):
        problems.append(f"{pdf_path.name}: does not start with a %PDF header")
        return problems

    # 2. pypdf can open it, count pages, and extract text.
    try:
        reader = PdfReader(str(pdf_path))
        pages = reader.pages
        page_count = len(pages)
    except Exception as exc:  # noqa: BLE001 - any parse failure is a problem
        problems.append(f"{pdf_path.name}: unreadable PDF ({type(exc).__name__}: {exc})")
        return problems

    if page_count < 1:
        problems.append(f"{pdf_path.name}: PDF has no pages")
        return problems

    text = ""
    for page in pages:
        text += page.extract_text() or ""

    # 3. Text is actually present (not a blank render).
    if not text.strip():
        problems.append(f"{pdf_path.name}: PDF contains no extractable text")

    # 4. Every expected sheet title made it into the render.
    if src_dir is not None:
        title = expected_title(src_dir / f"{pdf_path.stem}.html")
        if title and title.lower() not in text.lower():
            problems.append(f"{pdf_path.name}: expected title {title!r} not found in PDF text")

    # 5. Unbranded: no company name on the printed sheet.
    lowered = text.lower()
    for brand in BRAND_STRINGS:
        if brand.lower() in lowered:
            problems.append(f"{pdf_path.name}: appears branded ({brand} found) - must be unbranded")

    # 6. External links would phone home; the kit should be fully local/offline.
    for page in pages:
        annotations = page.get("/Annots") or []
        for annot in annotations:
            obj = annot.get_object()
            action = obj.get("/A")
            if action and action.get("/URI"):
                problems.append(f"{pdf_path.name}: PDF contains an external URI link ({action.get('/URI')})")
                break
            dest = obj.get("/Dest")
            if isinstance(dest, str) and ("://" in unquote(dest) or unquote(dest).startswith("file://")):
                problems.append(f"{pdf_path.name}: PDF contains an external dest link")
                break

    # 7. No secrets-style strings that should never ship (defensive habit check).
    for pattern in (r"api[_-]?key", r"bearer\s+[A-Za-z0-9]", r"sk-[A-Za-z0-9]{10,}"):
        if re.search(pattern, text, re.IGNORECASE):
            problems.append(f"{pdf_path.name}: possible secret-like text found")

    return problems


def expected_title(html_path: pathlib.Path) -> str:
    """Pull the <title> from a sheet's HTML, if present."""
    if not html_path.exists():
        return ""
    match = re.search(r"<title>(.*?)</title>", html_path.read_text(encoding="utf-8"), re.DOTALL)
    if not match:
        return ""
    title = re.sub(r"<[^>]+>", "", match.group(1))  # strip any tags out of the title
    title = (
        title.replace("&amp;", "&").replace("&middot;", "·").strip()
    )
    return title
