"""Screenshot chosen scenes at several device sizes and report broken files.

    python check_sizes.py URL OUT_DIR --scenes "#frame-16" "#frame-27" \
        --loader "document.querySelector('#appLoader')?.classList.contains('is-hidden')"

Default sizes: 1024x768 (4:3 tablet), 1280x800 (16:10 tablet), 812x375
(phone landscape). Output: OUT_DIR/screens/size_<w>x<h>_<scene>.png, plus
every HTTP >= 400 response and the smallest tappable-looking targets and
their spacing on each screen.
"""
import argparse
import re

from harness import Session

TARGETS_JS = r"""() => {
  const els = [...document.querySelectorAll('button,[role=button],[data-point],[class*=point],[class*=choice],[class*=island],[draggable]')]
    .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.width < 400; });
  const rs = els.map(e => { const r = e.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2, w: Math.round(r.width), h: Math.round(r.height), name: (e.dataset.point || e.getAttribute('aria-label') || e.className || e.tagName).toString().slice(0, 30) }; });
  let minGap = null;
  for (let i = 0; i < rs.length; i++) for (let j = i + 1; j < rs.length; j++) {
    const d = Math.hypot(rs[i].x - rs[j].x, rs[i].y - rs[j].y); if (d > 1 && (minGap === null || d < minGap)) minGap = Math.round(d); }
  rs.sort((a, b) => a.w * a.h - b.w * b.h);
  const vw = innerWidth, vh = innerHeight;
  const cut = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
    return r.width > 200 && r.height > 100 && cs.visibility !== 'hidden' && (r.bottom > vh + 2 || r.right > vw + 2) && r.top < vh; }).length;
  return { smallest: rs.slice(0, 4), minCentreGap: minGap, elementsPastViewport: cut };
}"""

ap = argparse.ArgumentParser()
ap.add_argument('url')
ap.add_argument('out')
ap.add_argument('--scenes', nargs='+', default=[''])
ap.add_argument('--loader', default=None)
ap.add_argument('--sizes', nargs='+', default=['1024x768', '1280x800', '812x375'])
ap.add_argument('--settle', type=float, default=9)
a = ap.parse_args()

for size in a.sizes:
    w, h = map(int, size.split('x'))
    for sc in a.scenes:
        with Session(a.url, a.out, w, h) as s:
            s.open(sc)
            s.wait_loaded(a.loader, settle=a.settle)
            tag = re.sub(r'\W+', '', sc) or 'start'
            s.snap(f'size_{w}x{h}_{tag}', f'{w}x{h} {sc}', delay=0)
            print('   targets:', s.page.evaluate(TARGETS_JS))
            print('   HTTP errors:', sorted(set(s.bad)))
