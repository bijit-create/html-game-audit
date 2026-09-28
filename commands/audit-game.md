---
description: Play an HTML learning game and mark the quality checklist, with screenshots
argument-hint: <game URL> [checklist.xlsx] [LP file]
---

Audit the HTML game at $ARGUMENTS against the quality checklist.

Use the `html-game-audit` skill and follow its steps in order: open the audit
log, read the source, play the game in the scripted browser (story frames,
every practice with idle / wrong / right probes, three screen sizes), keep a
screenshot for every step, mark all checklist items, build the filled
checklist workbook, and — if I say yes — put the screenshots and a Google
Sheet in my Drive.

If no checklist file is given, use the one bundled with the skill. If no LP
is given, mark the items that need it as Cannot mark and say so.
