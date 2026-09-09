"""Offline, responsive browser gate: uv run --with playwright tests/browser.py."""
from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
NEW = ['otto-gbdt-vs-dnn-ltr', 'multi-harness-rl', 'autolr-dashen',
       'sid-ope-hierarchy', 'walmart-demand-transfer', 'harness-r1']


def main():
    pages = sorted((SITE / 'papers').glob('*.html'))
    errors = []
    with sync_playwright() as pw:
        chrome = os.environ.get('CHROME_PATH') or ('/opt/google/chrome/chrome' if Path('/opt/google/chrome/chrome').exists() else None)
        browser = pw.chromium.launch(executable_path=chrome,
                                     args=['--no-sandbox', '--disable-dev-shm-usage'])
        for width in (360, 768, 1440):
            page = browser.new_page(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
            page.on('pageerror', lambda e: errors.append(str(e)))
            for path in pages:
                page.goto(path.as_uri())
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (path.name, width)
                assert page.locator('figure.teaching').count() >= 2
                assert page.locator('[data-ready=true]').count() == page.locator('[data-interactive]').count(), path.name
                for img in page.locator('img').all():
                    img.scroll_into_view_if_needed()
                    img.evaluate('(img)=>img.decode()')
                    assert img.evaluate('(i)=>i.complete && i.naturalWidth>0'), path.name
                assert page.locator('a[href^="#"]').evaluate_all('(links)=>links.every(a=>document.getElementById(a.hash.slice(1)))')
                for explorer in page.locator('[data-interactive=explorer]').all():
                    data = json.loads(explorer.locator('[data-results]').text_content())
                    slider = explorer.get_by_role('slider')
                    slider.focus(); slider.press('End')
                    assert int(slider.input_value()) == len(data['frames'])-1
                    values = explorer.locator('.bar-label strong').all_text_contents()
                    assert [float(v.replace(',', '')) for v in values] == [round(b['value'], 4) for b in data['frames'][-1]['bars']]
                    explorer.get_by_role('button', name='初期条件に戻す', exact=True).click()
                    assert int(slider.input_value()) == data['default']
                if path.stem in NEW and width in (360, 1440):
                    page.locator('figure.paper-svg').first.screenshot(path=f'/tmp/{path.stem}-{width}.png')
            page.goto((SITE/'index.html').as_uri())
            assert page.locator('[data-paper]:visible').count() == len(pages)
            page.get_by_role('searchbox').fill('2609.04518')
            assert page.locator('[data-paper]:visible').count() == 1
            page.get_by_role('searchbox').fill('no-such-paper-xyz')
            assert page.locator('[data-empty]').is_visible()
            page.get_by_role('button', name='条件を消去').click()
            assert page.locator('[data-paper]:visible').count() == len(pages)
            page.close()
        nojs = browser.new_page(java_script_enabled=False, viewport={'width': 360, 'height': 900})
        for slug in NEW:
            nojs.goto((SITE/'papers'/f'{slug}.html').as_uri())
            assert nojs.locator('[data-fallback]:visible').count() == nojs.locator('[data-interactive]').count()
            assert nojs.evaluate('document.documentElement.scrollWidth <= innerWidth')
        # SVG text must stay inside its viewport at native geometry.
        svg_page = browser.new_page()
        for slug in NEW:
            for svg in (ROOT/'papers'/slug/'figures').glob('*.svg'):
                svg_page.goto(svg.as_uri())
                clipped = svg_page.evaluate('''() => {
                    const v=document.documentElement.viewBox.baseVal;
                    return [...document.querySelectorAll('text')].filter(t=>{
                      const b=t.getBBox();return b.x<0 || b.y<0 || b.x+b.width>v.width+1 || b.y+b.height>v.height+1;
                    }).map(t=>t.textContent);
                }''')
                assert not clipped, (svg, clipped)
        assert not errors, errors
        browser.close()
    print(f'PASS: {len(pages)} Labs × 3 widths; figures, sliders, filters, no-JS, SVG bounds')


if __name__ == '__main__':
    main()
