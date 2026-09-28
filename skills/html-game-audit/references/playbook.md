# Playbook: reading the game and driving it

Lessons from the first audits. Follow these before improvising.

## 1. Read the source first (10 minutes saves an hour)

```bash
curl -sS URL -o index.html
grep -oE '<script[^>]*src="[^"]+"' index.html        # the game scripts
curl -sS URL/script.js -o script.js                   # each script
curl -sS URL/locales.json -o locales.json             # text files if any
```

Find, and write down in the log doc:

- **Scene list** – an array of scene names or numbers, `showScene(n)`.
- **Jump to a scene** – a `#frame-N` hash, `?scene=`, `?dev=1` dev nav. Use
  it to open each practice directly instead of replaying the story.
- **Loader done condition** – the class or flag set when loading ends
  (e.g. `#appLoader.is-hidden`). Pass it as `--loader`.
- **Feedback sound function** – e.g. `playFeedbackSound('incorrect')`.
  Pass it to `hook_sounds` so right/wrong sounds are logged.
- **Narration** – recorded clips (`new Audio('audio/…')`) vs
  `speechSynthesis` (device voice). Note which lines use which.
- **Idle / hint timers** – `setTimeout` near words like nudge, hint, ghost,
  glow, idle. Comments often say plainly what help exists.
- **Answer logic** – what counts as correct for each practice. This is how
  "any drag that ends on B is accepted" was found.
- **Network calls** – `fetch`, `XMLHttpRequest`, `postMessage`, `sendBeacon`.
  None except loading files = no result reporting.

All text in a locales file can be quoted directly for items 21, 26, 27.

## 2. Headless browser pitfalls

| Symptom | Cause | Fix (already in harness.py) |
| --- | --- | --- |
| `page.goto` times out on `load` / `networkidle` | Slow or hanging third-party requests | `wait_until='commit'`, then wait on the loader condition |
| `page.screenshot` times out "waiting for fonts" | Web fonts from another host never arrive | Abort every request to another host |
| First load takes minutes | Large assets | Local cache; the second run is seconds |
| "Loading 100%" text still found after load | Loader hidden with a class, not removed | Wait on the class, not the text |
| Narration ends instantly | Headless has no real speech output | Treat audio timing as unverified; confirm in code |

Do not bypass the sandbox to fix a timeout. The fixes above were enough.

## 3. Driving practices

- Get coordinates from the DOM (`s.centre(selector, i)`), never guess
  pixels. A guessed "empty space" tap landed on a house in the first audit.
- Before calling something empty space, check `document.elementFromPoint`.
- For drag tasks use `s.drag(a, b)`; for "detour" use `via=`.
- After every action print `s.sounds[-3:]` – a correct action followed by
  `incorrect` is the most important bug class this audit finds.
- Re-run any surprising result once before logging it.
- Many games ignore input while narration plays. That is item 31 (no
  response to an action), not a harness fault – but confirm in the code.

## 4. Screen sizes

Run `check_sizes.py` on the first practice and the densest one. Look at the
screenshots, not just the numbers: letterboxing can hide a cut-off board.
`minCentreGap` under ~40 px on a phone is a likely item-30 failure.

## 5. Screenshots

Name them `<activity>_<nn>_<what>.png` (e.g. `s19_03_first_house.png`) and
`story_<scene>_<nn>.png`. Look at every screenshot you cite before citing
it – a file named for the ray frame turned out to be the cloud transition.
