# html-game-audit

A Claude Code / Cowork plugin that audits an HTML learning game against the
ConveGenius **Quality Checklist for HTML / FLN Games** by playing it.

Give it a game URL. It:

1. Opens an audit log and writes every step into it as it goes.
2. Reads the game's source to map the scenes, the answer logic, the hints and
   which lines are recorded or read by the device voice.
3. Plays the game in a scripted Chromium browser: watches every story frame,
   and drives every practice with five probes – tap during the intro, idle,
   three kinds of wrong answer, a right answer done badly (detour, reverse,
   tap-everything) and the clean right answer – logging the feedback sound
   after each action.
4. Repeats key screens at 4:3 tablet, 16:10 tablet and phone sizes.
5. Saves a screenshot for every step.
6. Marks all checklist items (Meets / Does not meet / Cannot mark), with the
   scene, the exact on-screen words, a correction and up to three
   screenshots each, and flags the items that should block release.
7. Writes a copy of the checklist workbook filled in, plus a "Not covered by
   checklist" tab and a screenshot index.
8. Optionally uploads the screenshots to Google Drive and turns the workbook
   into a Google Sheet whose rows link to them.

## Install

```bash
claude plugin marketplace add bijit-create/html-game-audit
claude plugin install html-game-audit@html-game-audit
```

The scripts need Python 3.10+ with Playwright and openpyxl:

```bash
pip install playwright openpyxl
python -m playwright install chromium
```

Google Drive upload needs the Google Drive connector and the Claude in
Chrome extension, signed in to the Drive account.

## Use

```
/audit-game https://example.netlify.app/
```

or just ask: "Audit this game against the checklist: <url>". Add the LP /
skill statement if you have it; without it, the items that depend on it are
marked Cannot mark.

## What is in here

| Path | What it is |
| --- | --- |
| `skills/html-game-audit/SKILL.md` | The workflow Claude follows, step by step |
| `skills/html-game-audit/references/marking-rules.md` | Statuses, evidence rules, what blocks release, which probe feeds which item |
| `skills/html-game-audit/references/playbook.md` | Reading the source, headless-browser pitfalls and fixes, driving practices |
| `skills/html-game-audit/references/drive-upload.md` | Getting screenshots and the sheet into Google Drive via Chrome |
| `skills/html-game-audit/scripts/harness.py` | Playwright session: local cache, blocks other hosts, screen-state reader, sound logging, tap/drag/idle |
| `skills/html-game-audit/scripts/capture_story.py` | Watches the game and screenshots every change |
| `skills/html-game-audit/scripts/practice_template.py` | Template for driving one practice with the five probes |
| `skills/html-game-audit/scripts/check_sizes.py` | Screenshots at three sizes, target sizes/spacing, HTTP errors |
| `skills/html-game-audit/scripts/fill_checklist.py` | Fills the checklist workbook from `marks.json`, with optional Drive links |
| `skills/html-game-audit/assets/Quality Checklist for FLN Games.xlsx` | The checklist used by default |
| `skills/html-game-audit/assets/marks_template.json` | Shape of the marks file |
| `skills/html-game-audit/assets/example-points-game/` | The marks from the first real audit (Points game), as a worked example |

## Test the sheet builder

```bash
cd skills/html-game-audit
python scripts/fill_checklist.py "assets/Quality Checklist for FLN Games.xlsx" \
  assets/example-points-game/marks.json out.xlsx
```

Expected: `saved out.xlsx {'Cannot mark': 5, 'Does not meet': 13, 'Meets': 15, ...}`.
