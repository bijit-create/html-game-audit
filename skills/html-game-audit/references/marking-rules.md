# Marking rules

How to turn what was observed into a mark for each checklist item. The
checklist itself is `assets/Quality Checklist for FLN Games.xlsx`, tab
"HTML Quality Checklist", 35 items. Read the statements from the file every
run; do not rely on this page for their wording.

## The three statuses

| Status | Use when |
| --- | --- |
| Meets | Every screen the item applies to was checked and passes. |
| Does not meet | At least one screen fails. Name the scene, the action and the result. |
| Cannot mark | The item says "in the framework", "as defined in the LP" or depends on a target grade or device that was not given, and the LP / skill statement was not supplied. Say what input is missing. |

A qualifier is allowed after "Does not meet" when the failure is limited to a
condition: `Does not meet (phone)`, `Does not meet (4:3)`. Never add a
fourth status such as "Partly meets".

Never mark Meets for something that does not exist in the game. If an item
only applies "where required" and the game has no such element, write
Meets with the observation "Not present in this game; not required without
an LP" — or Cannot mark if the LP would decide it.

## Evidence

- Every Does not meet cites a scene number and at least one screenshot file.
- Quote on-screen text exactly, in double quotes.
- When a finding comes from reading the code rather than playing, say
  "the code shows …". Do not present a code reading as something seen.
- A finding that could be a harness artefact (timing, audio, autoplay) must
  be reproduced a second time or confirmed in the source before it is used.

## Blocking items

Mark `"blocks": true` (the sheet shows BLOCKS RELEASE in bold) when:

1. **Correct action gets wrong feedback, or wrong action gets praise** (item 24).
2. **The task can be finished without the target skill** (item 2): a detour
   accepted as "shortest path", tap-everything succeeds, answer can be read
   off colour or position (item 23).
3. **A concept the game teaches is never practised or checked** (item 8).
4. **A practice has no help at all** for a child who is stuck (item 15).
5. **A fact, example or answer key is wrong** (item 3).

Everything else is fix-before-release but not blocking.

## Which items need which probe

| Items | Evidence comes from |
| --- | --- |
| 1, 4, 5, 18, 19 | The LP / skill statement. Without it: Cannot mark. |
| 2, 23 | The "right answer done badly" probe and a look for visual give-aways. |
| 3, 6, 7, 22 | Story frames + every definition and picture; read locales / text files. |
| 8–14 | The whole scene map: what is taught, in what order, what is practised. |
| 15, 20 | The idle probe (30+ s) and the escalating-wrong-answer probe. |
| 16, 25 | The wrong-answer probes: is retry allowed, when is the answer shown, what does feedback say. |
| 17 | The end screen. |
| 21, 26, 27 | Every instruction, banner vs voice, the words used for objects and actions. |
| 24 | Sound log (`hook_sounds`) after every action, right and wrong. |
| 28, 33 | Which lines are recorded vs text-to-speech vs silent; any replay control. |
| 29–31 | Tap during intro, tap on demo elements, target sizes from `check_sizes.py`. |
| 32 | Start / continue / retry / finish controls. |
| 34 | Is right/wrong shown by more than colour. |
| 35 | `check_sizes.py` at 4:3, 16:10 and phone. |

## Not covered by the checklist

Always check and list separately (the sheet has a tab for these):

- Does the game report a result to the platform (fetch/XHR/postMessage/SCORM/xAPI)?
- HTTP 404s and console errors on load.
- Load time and loader timeout behaviour.
- Developer navigation or URL tricks (`?dev=1`, `#frame-N`) that skip tasks.
- Recorded voice vs device text-to-speech, and mismatches between the two.
- Total session length.
