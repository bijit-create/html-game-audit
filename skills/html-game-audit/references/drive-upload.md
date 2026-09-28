# Putting the screenshots and the sheet in Google Drive

The Google Drive connector can create folders and small text files, but
uploading an image means pasting its whole base64 content into the call,
which is not practical for 20+ screenshots. The working route is the user's
own Chrome (Claude in Chrome extension), where they are already signed in.

Ask the user before uploading: it puts files in their Drive.

## Steps

1. **Create the folder** with the Drive connector:
   `create_file(title="<Game> – Audit Screenshots", contentMimeType="application/vnd.google-apps.folder")`
   Keep the returned folder id.

2. **Open the folder in Chrome**: `https://drive.google.com/drive/folders/<id>`.

3. **Add a file input to the page.** Drive has no `<input type=file>` until
   "New → File upload" is clicked, and that opens a native file picker the
   extension cannot use. So create one:
   ```js
   const i=document.createElement('input');i.type='file';i.multiple=true;
   i.id='claudeUp';i.setAttribute('aria-label','claude upload input');
   i.style.cssText='position:fixed;top:0;left:0;z-index:99999';
   document.body.appendChild(i);
   ```
   Then `find("claude upload input")` for its ref.

4. **Load the files into it** with `file_upload(ref, paths=[...])`. Keep
   each call under 10 MB (about 12 PNG screenshots).

5. **Drop them onto Drive** – Drive accepts a synthetic drop:
   ```js
   const files=[...document.getElementById('claudeUp').files];
   const dt=new DataTransfer(); files.forEach(f=>dt.items.add(f));
   const t=document.elementFromPoint(innerWidth*0.6, innerHeight*0.6);
   for (const type of ['dragenter','dragover','drop'])
     t.dispatchEvent(new DragEvent(type,{bubbles:true,cancelable:true,dataTransfer:dt}));
   ```
   Wait ~10 s, then repeat steps 4–5 for the next batch.

6. **Collect the file ids** with the Drive connector:
   `search_files("parentId = '<folder id>' and (title contains 'story' or title contains 'size')")`
   and similar queries by prefix. The connector returns only a few results
   per page, so query by prefix until every screenshot is found. Write
   `drive_ids.json`: `{"folder": "<id>", "files": {"name.png": "<id>"}}`.

7. **Build the sheet** with links: `fill_checklist.py … --drive drive_ids.json`.

8. **Upload the xlsx** the same way (steps 3–5) into My Drive or the folder.

9. **Convert to Google Sheets**: open
   `https://docs.google.com/spreadsheets/d/<xlsx file id>/edit` in Chrome
   (it opens in Office mode, with an "XLSX" badge), then File → "Save as
   Google Sheets" (`find("Save as Google Sheets menu item")`). A new tab
   opens with the Google Sheet; its URL is the link to give the user.
   HYPERLINK formulas, fills, bold and every tab carry over. The xlsx copy
   stays in Drive; tell the user it can be deleted.

   To check a cell, type its address in the Name box (top left, left of
   `fx`), never click into the grid and type – that writes into the cell.
   If it happens, Ctrl+Z at once.

If Chrome is not connected, stop after step 1, give the user the local xlsx
and the screenshots folder, and say which steps are left.
