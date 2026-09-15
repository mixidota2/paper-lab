"""New-batch browser checks; run with uv and an environment containing Playwright."""
from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ('oxygenrec-v2-idgr', 'recevolve-autonomous-rec', 'quasid-collision-qualified-sid')


def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH', '/opt/google/chrome/chrome'),
                                    args=['--no-sandbox', '--disable-dev-shm-usage'])
        for width in (360, 768, 1440):
            page = browser.new_page(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
            page.on('pageerror', lambda error: errors.append(str(error)))
            for slug in SLUGS:
                page.goto((ROOT / 'site/papers' / f'{slug}.html').as_uri())
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (slug, width)
                assert page.locator('article section').count() >= 12
                for link in page.locator('a').all():
                    href = link.get_attribute('href') or ''
                    if href and not href.startswith(('https:', 'http:', '#', 'mailto:')):
                        assert (ROOT / 'site/papers' / href.split('#')[0]).resolve().exists(), (slug, href)
                for img in page.locator('img').all():
                    img.scroll_into_view_if_needed()
                    img.evaluate('(img) => img.decode()')
                for explorer in page.locator('[data-interactive=explorer]').all():
                    data = json.loads(explorer.locator('[data-results]').text_content())
                    slider = explorer.get_by_role('slider')
                    slider.focus()
                    slider.press('Home')
                    for i, frame in enumerate(data['frames']):
                        if i:
                            slider.press('ArrowRight')
                        assert int(slider.input_value()) == i
                        values = explorer.locator('.bar-label strong').all_text_contents()
                        assert [float(v.replace(',', '')) for v in values] == [round(b['value'], 4) for b in frame['bars']]
                    explorer.get_by_role('button', name='初期条件に戻す', exact=True).click()
                    assert int(slider.input_value()) == data['default']
                if width in (360, 1440):
                    page.screenshot(path=f'/tmp/{slug}-{width}-page.png', full_page=True)
                    page.locator('figure.paper-svg').first.screenshot(path=f'/tmp/{slug}-{width}-figure.png')
            page.goto((ROOT / 'site/index.html').as_uri())
            for query in ('2607.24255', '2609.01622', '2603.00632'):
                page.get_by_role('searchbox').fill(query)
                assert page.locator('[data-paper]:visible').count() == 1
            page.close()
        page = browser.new_page(java_script_enabled=False, viewport={'width': 360, 'height': 900})
        for slug in SLUGS:
            page.goto((ROOT / 'site/papers' / f'{slug}.html').as_uri())
            assert page.locator('[data-fallback]:visible').count() == page.locator('[data-interactive]').count()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.close()
        page = browser.new_page()
        for slug in SLUGS:
            for svg in (ROOT / 'papers' / slug / 'figures').glob('*.svg'):
                page.goto(svg.as_uri())
                clipped = page.evaluate('''() => {
                    const v = document.documentElement.viewBox.baseVal;
                    return [...document.querySelectorAll('text')].filter(t => {
                        const b=t.getBBox(); return b.x<0 || b.y<0 || b.x+b.width>v.width+1 || b.y+b.height>v.height+1;
                    }).map(t => t.textContent);
                }''')
                assert not clipped, (svg.name, clipped)
        assert not errors, errors
        browser.close()
    print('PASS: 3 new Labs × 360/768/1440px; every explorer frame, keyboard/reset, local links, search, no-JS, 5 SVG bounds; no JS errors')


if __name__ == '__main__':
    main()
