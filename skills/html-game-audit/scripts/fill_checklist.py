"""Fill a copy of the quality checklist workbook from a marks JSON file.

    python fill_checklist.py CHECKLIST.xlsx marks.json OUT.xlsx [--drive drive_ids.json]

The checklist's own layout is kept. Columns are found by their header text,
so reordered or renamed-but-similar checklists still work:
  item number  : header "No."
  status       : header containing "Status"
  observation  : header containing "Observation"
  correction   : header containing "Correction"
Screenshot columns ("Screenshot 1..3") are added after the last used column.

marks.json (see assets/marks_template.json):
{
  "title": "Points Game (Basic Geometrical Ideas) - https://...",
  "note":  "Reviewed 28 Sep 2026. LP not available.",
  "items": { "1": {"status": "Cannot mark", "observation": "...",
                   "correction": "...", "screenshots": ["x.png"], "blocks": false}, ... },
  "not_covered": [ {"issue": "...", "evidence": "...", "fix": "...", "screenshots": []} ],
  "screenshot_notes": { "x.png": "what it shows" }
}
Status values: "Meets", "Does not meet" (optionally with a qualifier such as
"Does not meet (phone)"), "Cannot mark".

drive_ids.json (optional): {"folder": "<folder id>", "files": {"x.png": "<file id>"}}.
With it, every screenshot becomes a clickable Drive link and a "Screenshots"
tab lists them all. Without it, the file names are written as plain text.

The script refuses to write if any checklist item has no mark, so a sheet
never goes out with rows silently blank.
"""
import argparse
import copy
import json

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ap = argparse.ArgumentParser()
ap.add_argument('checklist')
ap.add_argument('marks')
ap.add_argument('out')
ap.add_argument('--drive', default=None)
ap.add_argument('--sheet', default=None, help='checklist tab name (default: first tab with a "No." header)')
a = ap.parse_args()

marks = json.load(open(a.marks, encoding='utf8'))
drive = json.load(open(a.drive, encoding='utf8')) if a.drive else None
FILL = {'Meets': 'FFE2F0D9', 'Does not meet': 'FFF8CBAD', 'Cannot mark': 'FFD9D9D9'}
BLUE = Font(name='Calibri', color='FF0563C1', underline='single')
WRAP = Alignment(wrap_text=True, vertical='top')


def file_url(name):
    return f"https://drive.google.com/file/d/{drive['files'][name]}/view"


def put_link(cell, name, label=None):
    if drive and name in drive['files']:
        cell.value = f'=HYPERLINK("{file_url(name)}","{label or name}")'
        cell.font = BLUE
    else:
        cell.value = name
    cell.alignment = WRAP


wb = openpyxl.load_workbook(a.checklist)
ws, hrow = None, None
for cand in ([wb[a.sheet]] if a.sheet else wb.worksheets):
    for r in range(1, 10):
        if str(cand.cell(r, 1).value).strip().lower() in ('no.', 'no', '#', 's.no', 'sr. no.'):
            ws, hrow = cand, r
            break
    if ws:
        break
if not ws:
    raise SystemExit('No checklist tab with a "No." header in column A.')

heads = {str(ws.cell(hrow, c).value or '').lower(): c for c in range(1, ws.max_column + 1)}
col = lambda word: next((c for h, c in heads.items() if word in h), None)
c_status, c_obs, c_fix = col('status'), col('observation'), col('correction')
if not all((c_status, c_obs, c_fix)):
    raise SystemExit(f'Could not find Status / Observation / Correction headers in row {hrow}: {list(heads)}')
c_shot = ws.max_column + 1
hdr_style = ws.cell(hrow, 1)._style
for k in range(3):
    c = ws.cell(hrow, c_shot + k, f'Screenshot {k + 1}')
    c._style = copy.copy(hdr_style)
    ws.column_dimensions[get_column_letter(c_shot + k)].width = 30

items = {str(k): v for k, v in marks['items'].items()}
rows = [r for r in range(hrow + 1, ws.max_row + 1) if ws.cell(r, 1).value not in (None, '')]
missing = [str(ws.cell(r, 1).value) for r in rows if str(ws.cell(r, 1).value) not in items]
if missing:
    raise SystemExit(f'No mark for checklist items: {", ".join(missing)}')

for r in rows:
    m = items[str(ws.cell(r, 1).value)]
    obs = m['observation']
    if m.get('blocks'):
        obs = 'BLOCKS RELEASE. ' + obs
    for c, v in ((c_status, m['status']), (c_obs, obs), (c_fix, m.get('correction', ''))):
        cell = ws.cell(r, c, v)
        cell.alignment = WRAP
    key = next((k for k in FILL if m['status'].startswith(k)), 'Does not meet')
    ws.cell(r, c_status).fill = PatternFill('solid', fgColor=FILL[key])
    if m.get('blocks'):
        ws.cell(r, c_status).font = Font(name='Calibri', bold=True)
    for k, name in enumerate(m.get('screenshots', [])[:3]):
        put_link(ws.cell(r, c_shot + k), name)

if marks.get('title'):
    ws.cell(1, 2).value = f"Quality Checklist for {marks['title']}"
if marks.get('note'):
    ws.cell(1, c_obs).value = marks['note']
    ws.cell(1, c_obs).alignment = WRAP
if drive:
    folder = f"https://drive.google.com/drive/folders/{drive['folder']}"
    ws.cell(1, c_fix).value = f'=HYPERLINK("{folder}","All screenshots (Drive folder)")'
    ws.cell(1, c_fix).font = BLUE

# Issues the checklist has no row for
nc = wb.create_sheet('Not covered by checklist', wb.sheetnames.index(ws.title) + 1)
nc.append(['Issue', 'Evidence', 'Suggested fix', 'Screenshot 1', 'Screenshot 2'])
for c in nc[1]:
    c._style = copy.copy(hdr_style)
for row in marks.get('not_covered', []):
    nc.append([row['issue'], row.get('evidence', ''), row.get('fix', '')])
    r = nc.max_row
    for c in range(1, 4):
        nc.cell(r, c).alignment = WRAP
    for k, name in enumerate(row.get('screenshots', [])[:2]):
        put_link(nc.cell(r, 4 + k), name)
for letter, w in zip('ABCDE', (60, 50, 45, 28, 28)):
    nc.column_dimensions[letter].width = w

# Screenshot index
used = sorted({n for m in items.values() for n in m.get('screenshots', [])} |
              {n for row in marks.get('not_covered', []) for n in row.get('screenshots', [])})
sh = wb.create_sheet('Screenshots', wb.sheetnames.index(nc.title) + 1)
sh.append(['File', 'What it shows', 'Link'])
for c in sh[1]:
    c._style = copy.copy(hdr_style)
notes = marks.get('screenshot_notes', {})
for n in used:
    sh.append([n, notes.get(n, '')])
    put_link(sh.cell(sh.max_row, 3), n, 'Open')
for letter, w in zip('ABC', (34, 55, 12)):
    sh.column_dimensions[letter].width = w

wb.save(a.out)
from collections import Counter
print('saved', a.out, dict(Counter(items[str(ws.cell(r, 1).value)]['status'] for r in rows)))
if drive:
    lost = [n for n in used if n not in drive['files']]
    if lost:
        print('WARNING: not uploaded to Drive, written as plain names:', lost)
