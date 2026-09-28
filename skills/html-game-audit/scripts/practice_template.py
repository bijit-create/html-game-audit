"""Template for driving ONE practice activity. Copy it per activity and edit
the marked parts after reading that activity's code.

Every practice gets the same five probes, in this order, each with a
screenshot. These are what the checklist items need as evidence:

  1. tap_during_intro  - input while narration/intro plays   (item 31)
  2. idle              - no input for 30+ s at the prompt     (items 15, 20)
  3. wrong answers     - at least three different wrong kinds (items 16, 24, 25)
                         e.g. empty space, a distractor, the right object
                         dropped in the wrong place
  4. right answer done "badly" - e.g. a detour drag, reverse order,
                         tapping everything                   (items 2, 23)
  5. right answer      - the clean correct action             (item 24)

Watch self.sounds after each action: a correct action that logs an
'incorrect' sound (or shows "Oops") is a blocking item-24 failure.

    python practice_template.py URL OUT_DIR
"""
import sys
import time

from harness import Session

URL, OUT = sys.argv[1], sys.argv[2]
SCENE = '#frame-16'                      # EDIT: how to jump to this activity
LOADER = "document.querySelector('#appLoader')?.classList.contains('is-hidden')"  # EDIT
SOUND_FN = 'playFeedbackSound'           # EDIT: global feedback-sound function, or None
P = 's16'                                # EDIT: screenshot prefix for this activity

with Session(URL, OUT) as s:
    s.open(SCENE)
    s.wait_loaded(LOADER, settle=1)
    if SOUND_FN:
        s.hook_sounds(SOUND_FN)
    s.snap(f'{P}_01_start', 'activity opens')

    # EDIT: find targets from the DOM, e.g. s.centre('.house-choice', 0)
    board = s.page.evaluate("(()=>{const r=document.querySelector('#board, .board, svg')?.getBoundingClientRect();return r?[r.x,r.y,r.width,r.height]:null})()")
    print('board', board)

    # 1. tap during intro / narration
    s.tap((board[0] + 200, board[1] + 150))
    s.snap(f'{P}_02_tap_during_intro', 'tap while the instruction is still playing')

    # 2. idle
    time.sleep(6)
    s.idle(45, every=15, prefix=f'{P}_03_idle')

    # 3. wrong answers (EDIT: at least three different kinds)
    # s.tap(empty_space);           s.snap(f'{P}_04_wrong_empty', 'tap empty space')
    # s.drag(a, distractor);        s.snap(f'{P}_05_wrong_distractor', 'drag to a distractor')
    # s.drag(a, distractor); time.sleep(3); s.snap(f'{P}_06_after_two_wrong', 'help after two misses?')

    # 4. right answer done badly (EDIT)
    # s.drag(a, b, via=(midx, midy - 150)); s.snap(f'{P}_07_detour', 'correct end points, long detour')

    # 5. right answer
    # s.drag(a, b); s.snap(f'{P}_08_correct', 'clean correct action')
    time.sleep(4)
    s.snap(f'{P}_09_after', 'what happens next')
    print('sounds:', s.sounds)
    print('\n'.join(s.log))
