"""Watch the game without touching it and screenshot every change.

Takes a screenshot whenever the visible text, the scene variable or the page
hash changes, and stops when a stop condition is met or time runs out. Use it
for the story / demonstration frames between practices, and to find where
the game stops and waits for the child.

    python capture_story.py URL OUT_DIR --start "#frame-1" --max 400 \
        --loader "document.querySelector('#appLoader')?.classList.contains('is-hidden')" \
        --stop "window.scene===16"

Output: OUT_DIR/screens/story_<scene>_<n>.png and one line per change on
stdout (elapsed seconds, file, visible text, audio state). Frames that
advance on their own and frames that stall are both visible from the log.
"""
import argparse
import json
import time

from harness import Session

ap = argparse.ArgumentParser()
ap.add_argument('url')
ap.add_argument('out')
ap.add_argument('--start', default='')
ap.add_argument('--loader', default=None)
ap.add_argument('--stop', default=None, help='JS expression; capture ends when true')
ap.add_argument('--max', type=int, default=300, help='seconds')
ap.add_argument('--stall', type=int, default=45, help='end if nothing changes for this many seconds')
ap.add_argument('--width', type=int, default=1024)
ap.add_argument('--height', type=int, default=768)
ap.add_argument('--prefix', default='story')
a = ap.parse_args()

with Session(a.url, a.out, a.width, a.height) as s:
    s.open(a.start)
    s.wait_loaded(a.loader, settle=0.5)
    t0 = time.time(); last = None; n = 0; changed = time.time()
    while time.time() - t0 < a.max:
        st = s.state()
        key = json.dumps([st.get('scene'), st.get('text'), st.get('hash')], ensure_ascii=False)
        if key != last:
            n += 1
            time.sleep(1.2)  # let the entrance animation land
            s.snap(f"{a.prefix}_{st.get('scene')}_{n:02d}", f't={round(time.time() - t0)}s', delay=0)
            last = key; changed = time.time()
        if a.stop and s.page.evaluate(a.stop):
            print('stop condition met'); break
        if time.time() - changed > a.stall:
            s.snap(f"{a.prefix}_{st.get('scene')}_stalled", f'no change for {a.stall}s: waiting for the child?', delay=0)
            break
        time.sleep(0.8)
    print('\n'.join(s.log))
    print('HTTP errors:', s.bad)
