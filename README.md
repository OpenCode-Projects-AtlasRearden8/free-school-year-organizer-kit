# Free School Year Organizer Kit

Eight unbranded, print-and-go PDF organizers that help a regular parent tame the
school year from the first week of paperwork to the end-of-year binder cleanout.
Zero signups, zero tracking, zero cost. Build them yourself on your own machine
with one script.

**Built for the household. Built locally. No accounts, no ads, no phone-home.**

Copyright (c) 2026 Asdale Dynamics, LLC. Released under the MIT license —
see [LICENSE](LICENSE).

## What's inside

The finished PDFs live in [`printables/`](printables/) — the editable,
human-readable HTML/CSS sources live in [`src/`](src/). Each sheet includes a
friendly "How to use this sheet" parent guide right on it — the only reading
it ever asks of you.

| # | Sheet | The problem it kills |
|---|-------|----------------------|
| 1 | First-Week Paperwork Checklist | The avalanche of forms the first week — with due-date blanks and a place for the surprise extras |
| 2 | Teacher Contact Tracker | "I know I emailed someone about this..." — every adult worth knowing, in one tidy table |
| 3 | Backpack Folder Map | The black-hole backpack — a four-folder color system and a 2-minute nightly empty-out routine |
| 4 | Permission-Slip & Field-Trip Log | Ten blinking permission slips a year — one line each, signed and paid, nothing late |
| 5 | Activities & Fees Calendar | The surprise $200 activity month — every club, season, and fee visible at once (two-page sheet) |
| 6 | Lunch Balance Sweep Card | The "your child owes $23" email — one five-minute sweep a month, logged in ink |
| 7 | Sick-Day Readiness Sheet | The 6:15 a.m. scramble — numbers, rules, and the day-used log filled in while everyone is healthy |
| 8 | End-of-Year Binder Cleanout Ritual | Eleven months of paper in a drawer gone forgotten — a two-hour send-off ritual, one memory box per kid |

Twenty minutes of quiet Sunday, and the paperwork year is basically on rails.

## How to build

Requirements: Python 3.9+ and [WeasyPrint](https://weasyprint.org/) (a local,
offline HTML→PDF engine — no network is used by this project).

```bash
pip install weasyprint     # once
python3 build.py           # rebuild all 8 PDFs into printables/ + verify
```

Options:

- `python3 build.py --out /tmp/mine` — write the PDFs anywhere you like
- `python3 build.py --skip-verify` — build without the PDF sanity checks

Verified PDFs land in `printables/`, ready to print on US Letter (also fine
on A4 — WeasyPrint honors the stylesheet's Letter size; scale to fit if needed).
Every sheet is designed to read well in plain black-and-white home printing.

## Validating your build

Two ways, both offline:

```bash
python3 build.py                    # builds, then quick-verifies every PDF
python3 tests/test_build.py          # full test suite (unittest)
# or: python3 -m unittest discover tests
```

The tests check that all eight sheets build, every PDF is a valid multi-page
PDF with real text, the sheets stay unbranded, no external links phone home,
no secrets sneak into the repo, and `printables/` contains exactly the
expected files.

## Using the kit

Print sheets 1 and 6–7 on cardstock or fridge-paper and pin them up; sheets
2–5 belong in one home-school binder grouped behind the backpack-folder map
(sheet 3) as a divider page. Reprint a fresh copy each child, each year —
the HTML sources make rebranding (to your family's name) and reprinting trivial.

## Project layout

```
src/          HTML + CSS sources — the sheets as real, editable files
printables/   Finished PDFs (unbranded, ready to share or print)
tests/        PDF validity checks + build test suite
build.py      One-command local build (WeasyPrint)
```

No signups. No telemetry. No network at build time.

## About

A practical life-admin helper from [Asdale Dynamics, LLC](https://dylanasdale.github.io)
— Dylan Asdale's beginner-friendly AI education hub — designed in the same plain,
warm, step-by-step style as *The Massive AI Manual*: talk to a parent like a
friend would.

Suggestions and fixes are welcome. If this saved you a morning, tell another
parent — that's the whole business model.

## License

MIT — see [LICENSE](LICENSE). Educational organizer only; nothing here is
medical advice.
