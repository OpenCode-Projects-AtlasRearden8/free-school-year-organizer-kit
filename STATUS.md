# STATUS: Free School Year Organizer Kit

Date: 2026-10-30
Owner: Asdale Dynamics, LLC (Dylan Asdale)

## What was built

Eight unbranded, print-and-go school-year organizers for parents, delivered as
printable PDFs built from editable HTML/CSS sources. Every sheet carries a
friendly "How to use this sheet" parent guide printed right on it. Zero
signups, zero tracking, fully local/offline build.

1. `01-first-week-checklist` — first-week paperwork checklist with due-date blanks
2. `02-teacher-contact-tracker` — teacher & staff contact table with last-contact log
3. `03-backpack-folder-map` — four-folder color system + 2-minute nightly empty-out routine
4. `04-permission-slip-log` — one-line-per-field-trip log (cost, paid, signed, packed-for)
5. `05-activities-fees-calendar` — fall/winter + spring/summer activity & fee tables (2 pages)
6. `06-lunch-balance-card` — monthly 5-minute lunch-balance sweep log (Sept–June)
7. `07-sick-day-readiness` — sick-day numbers/rules filled in ahead + day-used log
8. `08-binder-cleanout` — end-of-year cleanout ritual in four parts, one memory box per kid (2 pages)

Repository layout:

- `src/` — 8 HTML sheets + shared `print.css` (letter-size, B&W-friendly)
- `printables/` — the 8 finished unbranded PDFs (the deliverable)
- `build.py` — one-command local build (WeasyPrint HTML→PDF), with `--out` and `--skip-verify`
- `tests/` — `verify_pdfs.py` (PDF validity checks) + `test_build.py` (12-test unittest suite)
- `README.md`, `LICENSE` (MIT, Copyright (c) 2026 Asdale Dynamics, LLC)

## How to run it

```bash
pip install weasyprint    # version tested: 70.0
python3 build.py          # builds all 8 PDFs into printables/ and verifies them
python3 tests/test_build.py   # full test suite (also: python3 -m unittest discover tests)
```

Build options: `--out DIR` to write elsewhere, `--skip-verify` to skip checks.

## Verification results (2026-10-30)

- `python3 build.py` → 8/8 sheets built, 8/8 PDFs verified valid
  (valid `%PDF` header, pypdf-parseable, real extractable text, expected sheet
  title present, unbranded, no external URI links, no secret-like strings)
- PDF page counts sane: sheets 5 and 8 are 2 pages by design, the rest are 1
- Test suite: 12/12 passed (`python3 tests/test_build.py` and
  `python3 -m unittest discover tests` both OK)
- No CJK/garbled characters in sources or rendered text (regex-checked)
- Confirmed house rules: no network calls at build or in output, no branding in
  `printables/`, no secrets, license copyright line exact
- Sources deliberately contain no `http://` or `https://` links (tested)

## Known gaps / future ideas

- Letter-page sizing only; A4 prints fine scaled but dedicated A4 CSS is not provided
- No dark/print-style variants — sheets are intentionally single-style B&W
- No Spanish-language versions (a natural kit v2: translated sheets)
- Fill-in text fields are for handwriting only; no interactive PDF form fields yet
- WeasyPrint is the only supported engine (Chrome/puppeteer path not provided)
- Not git-initialized anywhere remote — repo is local-only by design; nothing pushed or published
