---
name: html-game-audit
description: Audit an HTML learning game (a URL) against the ConveGenius "Quality Checklist for HTML/FLN Games" by actually playing it in a scripted browser — story frames watched, every practice driven with idle, wrong, badly-done-right and right answers, three screen sizes — with a screenshot for every step. Produces a step-by-step audit log doc, the checklist workbook filled in (Status, Observation, Correction, screenshot links, blocking flags, a "Not covered" tab), and optionally the screenshots and sheet in Google Drive as a Google Sheet. Use when someone says "audit this game", "check this HTML against the checklist", "mark the checklist for <url>", "QA this LBD / game build", or pastes a game URL and asks how it scores. Do not use for question-bank CSVs (clms question-audit) or for storyboards on paper (pal-lbd lbd-review).
---

# HTML game audit

Play the game the way a reviewer would, mark every checklist item from what
was seen, and hand back evidence someone else can check.

Inputs:
- **Game URL** (required).
- **Checklist workbook** – default `assets/Quality Checklist for FLN Games.xlsx`;
  use the user's file if they give one.
- **LP and skill statement** (optional). Without them, items that depend on
  them are marked Cannot mark – say so up front.
- **Where the results go** – ask once: local files only, or also Google
  Drive (needs the Claude in Chrome extension; see `references/drive-upload.md`).

Outputs, in a work folder `<cwd>/<game-slug>-audit/`:
- `screens/` – every screenshot, named by scene and step.
- An **audit log doc** (Claude Docs if available, else `audit-log.md`) with
  every step in order, each citing its screenshot.
- `<Game> - Quality Checklist Review.xlsx` – the checklist filled in.
- Optionally the screenshots folder and a Google Sheet in Drive.

Read `references/playbook.md` and `references/marking-rules.md` before step 2.
Scripts are in `scripts/`; run them with `PYTHONIOENCODING=utf8` on Windows.
They need Python with `playwright` and `openpyxl` (`pip install playwright
openpyxl && python -m playwright install chromium` if missing).

## Step 0 – Open the log

Create the audit log first, with one pending section per heading below, so
the user can watch it fill: Setup · Walkthrough log · Checklist marking ·
Issues the checklist has no row for · Screenshot evidence. Fill each section
as soon as its content exists – write the walkthrough step by step while
playing, not at the end.

## Step 1 – Setup

Record: URL, checklist file and tab, device sizes used, and which inputs are
missing. Read the checklist statements from the workbook
(`openpyxl`, the tab with a "No." header). Keep the item numbers exactly as
the workbook has them.

## Step 2 – Read the source

Follow `references/playbook.md` §1. Save `index.html`, scripts and text files
into the work folder. From them write down the scene list, the jump-to-scene
mechanism, the loader condition, the feedback-sound function, which lines
are recorded vs text-to-speech, the hint/idle logic and the answer logic of
each practice. Put the scene map in the log.

## Step 3 – First load and idle

Load with no interaction (`capture_story.py URL OUT --loader …`). Note load
time, whether the game needs a first tap, and where it first waits for the
child. At that first practice, stay idle for at least 60 s with screenshots
every 15 s (the `--stall` end of `capture_story.py`, or `Session.idle`).

## Step 4 – Story and demonstration frames

`capture_story.py` between each pair of practices (`--start '#frame-N'
--stop …`). For every frame check: is the fact / picture right, is the text
read aloud, does the voice say what the banner says, does it tell the child
to do something that is not possible on that screen, how long is it shown.
Look at the screenshots.

## Step 5 – Each practice

Copy `scripts/practice_template.py` per practice and fill in the targets
from the DOM. Run the five probes in order: tap during intro · idle ·
three kinds of wrong answer · right answer done badly · clean right answer.
Log the sound after every action. Reproduce any surprising result once.
Write the practice into the log as numbered steps with screenshot names.

## Step 6 – Sizes and technical checks

`check_sizes.py URL OUT --scenes <first practice> <densest practice>`.
Also record HTTP errors, console errors, network calls (result reporting),
dev-navigation leaks, and total length.

## Step 7 – Mark the checklist

Write `marks.json` in the work folder using `assets/marks_template.json`
(worked example: `assets/example-points-game/marks.json`). Every item gets a
status, an observation with scene and quoted text, a correction, and up to
three screenshots. Apply `references/marking-rules.md` – three statuses
only, and the blocking rules. Add everything the checklist does not ask
about to `not_covered`.

Then put the same marking table into the log's "Checklist marking" section
and lead it with the count: "N Meets, N Does not meet, N Cannot mark; items
… block release."

## Step 8 – Build the sheet

```bash
python scripts/fill_checklist.py "<checklist.xlsx>" marks.json "<Game> - Quality Checklist Review.xlsx"
```
It refuses to write if any item is unmarked. Read the result back and check
a few rows.

## Step 9 – Drive (if asked)

Follow `references/drive-upload.md`: folder → screenshots → `drive_ids.json`
→ rebuild the sheet with `--drive drive_ids.json` → upload → Save as Google
Sheets. Embed the most important 5–8 screenshots in the log doc too.

## Step 10 – Report

Reply in a few lines: the counts, the blocking items in one line each, the
links (log doc, sheet, screenshots folder), and anything that could not be
checked (missing LP, audio heard only through code, a size not tested).

## Rules

- Mark only from what was seen or read in the code, and say which.
- Never cite a screenshot you have not looked at.
- Quote the game's words exactly; do not paraphrase an instruction you are judging.
- Do not bypass the sandbox or security prompts to make the browser work;
  the harness fixes are enough (see the playbook).
- Uploading to Drive or sharing anything is the user's call – ask first.
