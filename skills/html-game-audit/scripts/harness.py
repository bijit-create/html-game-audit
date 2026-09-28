"""Shared Playwright harness for auditing an HTML learning game.

Every other script imports this. It does four things the audit always needs:

1. Serves the game's own files from a local cache, so reruns load in seconds
   instead of minutes (a heavy game can take 4+ minutes on first load).
2. Aborts every request to another host. Web fonts from other hosts can hang
   page.screenshot() ("waiting for fonts to load") until it times out.
3. Records console errors, page errors and HTTP >= 400 responses.
4. Gives one `state()` call that reads what a child would see and hear:
   visible banner / instruction text and the narration element's state.

Usage from another script:

    from harness import Session
    with Session(url, out_dir) as s:
        s.open('#frame-16')          # hash or query appended to the URL
        s.wait_loaded()
        s.snap('s16_01_start', 'first look')

Environment: set PYTHONIOENCODING=utf8 on Windows so game text prints.
"""
import hashlib
import json
import os
import time
import urllib.parse

from playwright.sync_api import sync_playwright

# JavaScript run in the page to describe what is on screen. It is generic on
# purpose: it collects text from anything that looks like a banner, bubble,
# instruction or prompt, and the first <audio>/Audio narration it can find.
STATE_JS = r"""() => {
  // checkVisibility looks at ancestors too (a hidden scene hides its banner).
  const vis = e => { const r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight)) return false;
    if (e.checkVisibility) return e.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true });
    const cs = getComputedStyle(e); return cs.visibility !== 'hidden' && cs.opacity !== '0'; };
  const sel = '[class*=banner],[id*=anner],[class*=instruction],[id*=nstruction],[class*=bubble],[class*=prompt],[class*=dialog],[role=status],[aria-live]';
  const seen = new Set(); const texts = [];
  // Skip screen-sized wrappers (a whole-stage aria-live section would swallow
  // every scene's text), then keep the outermost of what is left so a banner
  // is read as one sentence, not word by word.
  const big = e => { const r = e.getBoundingClientRect(); return r.width * r.height > 0.5 * innerWidth * innerHeight; };
  const hits = [...document.querySelectorAll(sel)].filter(e => vis(e) && !big(e));
  hits.filter(e => !hits.some(o => o !== e && o.contains(e))).forEach(e => {
    const t = (e.innerText || '').trim().replace(/\s+/g, ' ');
    if (t && t.length < 400 && !seen.has(t)) { seen.add(t); texts.push(t); } });
  const audios = [...document.querySelectorAll('audio')];
  const a = audios.find(x => !x.paused) || audios[0];
  // A top-level `let scene` is not on window, so read it by global eval.
  let sc = null;
  try { sc = (0, eval)("typeof scene !== 'undefined' ? scene : (typeof currentScene !== 'undefined' ? currentScene : null)"); } catch (e) {}
  return { scene: sc, stageClass: (document.querySelector('#stage,main,body')?.className || '').slice(0, 120),
           text: texts.slice(0, 6), hash: location.hash,
           audio: a ? (a.src.split('/').pop() + (a.paused ? ' (paused)' : ' (playing)')) : '' };
}"""


class Session:
    def __init__(self, url, out_dir, width=1024, height=768, autoplay=True, cache_dir=None):
        self.url = url.rstrip('#')
        self.host = urllib.parse.urlparse(url).netloc
        self.out = out_dir
        self.shots = os.path.join(out_dir, 'screens')
        self.cache = cache_dir or os.path.join(out_dir, 'cache')
        os.makedirs(self.shots, exist_ok=True)
        os.makedirs(self.cache, exist_ok=True)
        self.size = (width, height)
        self.autoplay = autoplay
        self.log = []          # console / page errors
        self.bad = []          # (status, url) for HTTP errors
        self.sounds = []       # filled by hook_sounds()
        self.steps = []        # (name, note, state) for every snap

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self):
        self._p = sync_playwright().start()
        args = ['--autoplay-policy=no-user-gesture-required'] if self.autoplay else []
        self.browser = self._p.chromium.launch(args=args)
        self.page = self.browser.new_page(viewport={'width': self.size[0], 'height': self.size[1]})
        pg = self.page
        pg.on('console', lambda m: self.log.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: self.log.append(f'pageerror: {e}'))
        pg.on('response', lambda r: self.bad.append((r.status, r.url)) if r.status >= 400 else None)
        pg.route('**/*', self._route)
        return self

    def __exit__(self, *exc):
        with open(os.path.join(self.out, 'run_log.jsonl'), 'a', encoding='utf8') as f:
            for name, note, st in self.steps:
                f.write(json.dumps({'shot': name, 'note': note, 'state': st}, ensure_ascii=False) + '\n')
        self.browser.close()
        self._p.stop()

    # -- network -----------------------------------------------------------
    def _route(self, route):
        u = route.request.url
        if urllib.parse.urlparse(u).netloc != self.host:
            return route.abort()
        key = hashlib.md5(urllib.parse.urlparse(u).path.encode()).hexdigest()
        fn = os.path.join(self.cache, key)
        if os.path.exists(fn):
            meta = json.load(open(fn + '.json'))
            return route.fulfill(status=200, headers=meta, body=open(fn, 'rb').read())
        try:
            r = route.fetch(timeout=120000)
        except Exception:
            return route.abort()
        body = r.body()
        if r.status == 200:
            open(fn, 'wb').write(body)
            json.dump({k: v for k, v in r.headers.items() if k.lower() == 'content-type'}, open(fn + '.json', 'w'))
        return route.fulfill(response=r, body=body)

    # -- navigation --------------------------------------------------------
    def open(self, suffix=''):
        self.page.goto(self.url + suffix, wait_until='commit', timeout=120000)

    def wait_loaded(self, loader_js=None, timeout=300, settle=3):
        """Wait until the game's loader is gone.

        loader_js: a JS expression that is true once loading is done, taken from
        the game's source (for example
        "document.querySelector('#appLoader')?.classList.contains('is-hidden')").
        Do not test for the loader's text: many loaders stay in the DOM after
        they are hidden, so "Loading... 100%" is still readable.
        """
        if loader_js:
            self.page.wait_for_function(loader_js, timeout=timeout * 1000)
        else:
            self.page.wait_for_load_state('load', timeout=timeout * 1000)
        time.sleep(settle)

    # -- observation -------------------------------------------------------
    def state(self):
        try:
            return self.page.evaluate(STATE_JS)
        except Exception as e:  # page mid-navigation
            return {'err': str(e)}

    def snap(self, name, note='', delay=0.7):
        time.sleep(delay)
        self.page.screenshot(path=os.path.join(self.shots, f'{name}.png'))
        st = self.state()
        self.steps.append((name, note, st))
        print(f"{name} | {note} | {' / '.join(st.get('text', []))[:200]} | audio: {st.get('audio')} | sounds: {self.sounds[-3:]}", flush=True)
        return st

    def hook_sounds(self, fn_name):
        """Wrap a global feedback-sound function (found in the source, e.g.
        playFeedbackSound) so every call is logged in self.sounds. This is how
        a wrong-sound on a correct action gets caught."""
        self.page.expose_function('__auditSound', lambda k: self.sounds.append(k))
        self.page.evaluate(f"(()=>{{const o=window.{fn_name};if(!o)return 'missing';window.{fn_name}=(...a)=>{{__auditSound(String(a[0]));return o(...a)}};return 'ok'}})()")

    def centre(self, selector, index=0):
        """Centre point of the n-th element matching selector, in page pixels."""
        return self.page.evaluate(
            "([s,i])=>{const e=[...document.querySelectorAll(s)][i];if(!e)return null;const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}",
            [selector, index])

    # -- actions -----------------------------------------------------------
    def tap(self, xy):
        self.page.mouse.click(xy[0], xy[1])

    def drag(self, a, b, via=None, steps=12):
        """Press at a, move (optionally through via) and release at b."""
        m = self.page.mouse
        m.move(*a)
        m.down()
        if via:
            m.move(*via, steps=steps)
        m.move(*b, steps=steps)
        m.up()

    def idle(self, seconds, every=15, prefix='idle'):
        """Stay idle and screenshot at intervals, to test idle help."""
        t = 0
        while t < seconds:
            time.sleep(min(every, seconds - t))
            t += min(every, seconds - t)
            self.snap(f'{prefix}_{t:03d}s', f'idle {t}s', delay=0)
