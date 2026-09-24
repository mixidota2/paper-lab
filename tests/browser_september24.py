"""Responsive source-backed figures and every interactive state of the new Labs."""
import json
from pathlib import Path
from urllib.parse import urlparse, unquote
from playwright.sync_api import sync_playwright
from test_september24_labs import SLUGS
ROOT = Path(__file__).resolve().parents[1]

def main():
    errors, states = [], 0
    shots = Path('/tmp/lab-sep24'); shots.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/opt/google/chrome/chrome', args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in (360,390,768,1440):
            page = browser.new_page(viewport={'width': width,'height':900})
            page.on('pageerror', lambda e: errors.append(str(e)))
            for slug in SLUGS:
                page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), (slug,width)
                assert page.locator('.note-section').count() == 12
                assert page.locator('figure').count() >= 2
                assert page.locator('a[href^="#"]').evaluate_all('(a)=>a.every(x=>document.getElementById(x.hash.slice(1)))')
                for href in page.locator('a[href]').evaluate_all('(a)=>a.map(x=>x.href)'):
                    u = urlparse(href)
                    if u.scheme == 'file': assert Path(unquote(u.path)).is_file(), href
                for explorer in page.locator('[data-interactive=explorer]').all():
                    data = json.loads(explorer.locator('[data-results]').text_content())
                    slider = explorer.get_by_role('slider')
                    for i, f in enumerate(data['frames']):
                        slider.fill(str(i)); slider.dispatch_event('input')
                        values = explorer.locator('.bar-label strong').all_text_contents()
                        assert [float(v.replace(',','')) for v in values] == [round(b['value'],4) for b in f['bars']]
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                        states += 1
                    slider.focus(); slider.press('Home'); assert slider.input_value() == '0'
                    slider.press('End'); assert int(slider.input_value()) == len(data['frames'])-1
                    explorer.get_by_role('button',name='初期条件に戻す',exact=True).click()
                    assert int(slider.input_value()) == data['default']
                for w in page.locator('[data-b21]').all():
                    frames = json.loads(w.locator('[data-frames]').text_content())
                    for i, frame in enumerate(frames):
                        w.locator('select').select_option(str(i))
                        assert w.locator('[data-output]').inner_html() == page.evaluate('(s)=>{const d=document.createElement("div");d.innerHTML=s;return d.innerHTML}', frame)
                        states += 1
                for name in ['run.py','results.json','lab.yaml','README.md','method.md','mapping.md']:
                    assert (ROOT/'papers'/slug/name).read_bytes() == (ROOT/'site/downloads'/slug/name).read_bytes()
                if width in (360,1440):
                    page.screenshot(path=str(shots/f'{slug}-{width}.png'),full_page=True)
                    page.locator('figure').first.screenshot(path=str(shots/f'{slug}-figure-{width}.png'))
            page.goto((ROOT/'site/index.html').as_uri())
            for slug in SLUGS: assert page.locator(f'a[href="papers/{slug}.html"]').count() >= 1
            page.close()
        page = browser.new_page(java_script_enabled=False,viewport={'width':360,'height':900})
        for slug in SLUGS:
            page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for o in page.locator('[data-output]').all(): assert o.inner_text().strip()
            for fallback in page.locator('[data-fallback]').all(): assert fallback.is_visible()
        assert not errors, errors
        browser.close()
    print(f'PASS {len(SLUGS)} Labs × 4 widths; {states} states; keyboard, links, downloads, index, no-JS')

if __name__ == '__main__': main()
