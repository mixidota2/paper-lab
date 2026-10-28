"""Native-size viewport tiles for both article and standalone experiment pages."""
import base64
import hashlib
import json
from pathlib import Path
import struct
import time
from contextlib import contextmanager


def _capture(page, destination, region, horizontal, timings):
    """No resizing/stitching. A region limits vertical coverage, not pixel scale."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    with timed_phase(timings, "readiness"):
        page.evaluate("() => { for (const i of document.images) i.loading='eager'; }")
        page.wait_for_function("document.fonts.status==='loaded' && [...document.images].every(i=>i.complete && i.naturalWidth>0)")
    with timed_phase(timings, "dom_collection"):
        view = page.evaluate('({width:innerWidth,height:innerHeight,total:document.documentElement.scrollHeight,scrollWidth:document.documentElement.scrollWidth})')
        assert view['scrollWidth'] <= view['width'], view
        start, end = 0, view['total']
        if region is not None:
            box = region.bounding_box()
            assert box, 'Capture target is not visible'
            start = max(0, box['y'] + page.evaluate('scrollY') - 30)
            end = min(view['total'], start + box['height'] + 60)
        evidence = {'url': page.url, 'viewport': view, 'region': [start, end], 'tiles': [],
                    'manual_visual_review': 'NOT TESTED', 'method': 'native viewport, scale 1, >=100px overlap, no stitching',
                    'svg_geometry': page.locator('svg:visible').evaluate_all('(xs)=>xs.map(s=>({viewBox:s.getAttribute("viewBox"), width:s.getBoundingClientRect().width, height:s.getBoundingClientRect().height, text:s.textContent, polylines:[...s.querySelectorAll("polyline")].map(p=>p.getAttribute("points"))}))'),
                    'tables': page.locator('table:visible').evaluate_all('(xs)=>xs.map(t=>({text:t.innerText, width:t.clientWidth, scrollWidth:t.scrollWidth}))')}
    session = page.context.new_cdp_session(page)
    try:
        target = start
        for _ in range(100):
            with timed_phase(timings, "scroll_and_wait"):
                page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})', target)
                page.wait_for_timeout(50)
                pos = page.evaluate('({x:scrollX,y:scrollY})')
                if evidence['tiles']:
                    assert 0 < pos['y']-evidence['tiles'][-1]['y'] <= view['height']-99
            with timed_phase(timings, "screenshot"):
                raw = session.send('Page.captureScreenshot', {'format':'png','fromSurface':True,'captureBeyondViewport':False,
                    'clip':{'x':0,'y':pos['y'],'width':view['width'],'height':view['height'],'scale':1}})
            with timed_phase(timings, "decode_hash_write"):
                data = base64.b64decode(raw['data'])
                assert struct.unpack('>II', data[16:24]) == (view['width'], view['height'])
                name = f'{len(evidence["tiles"]):03d}.png'
                (destination/name).write_bytes(data)
                evidence['tiles'].append({**pos, 'file':name, 'sha256':hashlib.sha256(data).hexdigest()})
            if pos['y'] + view['height'] >= end-1:
                break
            target = pos['y'] + view['height'] - 100
        else:
            raise AssertionError('Capture exceeded 100 viewport tiles')
        with timed_phase(timings, "manifest_write"):
            (destination/'segments.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
    finally:
        with timed_phase(timings, "detach_restore"):
            session.detach()
            page.evaluate('scrollTo({top:0,behavior:"instant"})')
    with timed_phase(timings, "horizontal_children"):
        if horizontal:
            # Capture both ends of horizontal table scrollers without shrinking text.
            panels=page.locator('.matrix-scroll, .scroll, .reference-scroll, .tablewrap, .chart-data')
            for i,panel in enumerate(panels.all()):
                if not panel.is_visible() or not panel.evaluate('(e)=>e.scrollWidth>e.clientWidth+1'):continue
                old=panel.evaluate('(e)=>e.scrollLeft')
                try:
                    for side in ('left','right'):
                        panel.evaluate('(e,s)=>e.scrollLeft=s==="left"?0:e.scrollWidth',side)
                        capture(page,destination/f'table-{i}-{side}',panel,horizontal=False)
                finally:panel.evaluate('(e,x)=>e.scrollLeft=x',old)
    return evidence


@contextmanager
def timed_phase(timings, name):
    started = time.monotonic()
    try:
        yield
    finally:
        entry = timings.setdefault(name, {'count': 0, 'elapsed_s': 0.0})
        entry['count'] += 1
        entry['elapsed_s'] += max(0, time.monotonic() - started)


def capture(page, destination, region=None, horizontal=True):
    # Fixed phase keys/count aggregates only. Children have separate receipts;
    # horizontal_children is inclusive and must not be added to their totals.
    timings = {}
    started = time.monotonic()
    try:
        return _capture(page, destination, region, horizontal, timings)
    finally:
        receipt = {'elapsed_s': max(0, time.monotonic()-started), 'phases': timings}
        try:
            (Path(destination)/'capture-timing.json').write_text(json.dumps(receipt))
        except OSError:
            pass  # Diagnostic transport must never replace the original error.
