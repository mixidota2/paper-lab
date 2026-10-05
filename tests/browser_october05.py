"""Batch 2026-10-05: responsive interactive states and downloadable provenance."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['zalando-sales-event-pricing-forecast-optimize', 'exaone-demand-routed-tsfm', 'tsfm-sparse-event-ranking', 'agent-reasoning-forgetting-externalized-state']

def main():
    errors = []
    states = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/opt/google/chrome/chrome', args=['--no-sandbox', '--disable-dev-shm-usage'])
        for width in [360, 390, 768, 1440]:
            page = browser.new_page(viewport={'width': width, 'height': 900})
            page.on('pageerror', lambda e: errors.append(str(e)))
            for slug in SLUGS:
                page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
                assert page.locator('.note-section').count() == 12
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (slug, width)
                if slug.startswith('agent-reasoning'):
                    page.locator('[data-case]').select_option('prune_internal')
                    assert '再導出 4回' in page.locator('[data-summary]').inner_text()
                    page.locator('[data-case]').select_option('prune_external')
                    assert '再導出 0回' in page.locator('[data-summary]').inner_text()
                if slug.startswith('exaone'):
                    assert '25.0%' in page.locator('[data-weights]').inner_text()
                if slug.startswith('tsfm-sparse'):
                    page.locator('#sparse-p').fill('49')
                    page.locator('#sparse-p').dispatch_event('input')
                    assert page.locator('[data-mass] tbody td').nth(1).inner_text() == '0.0'
                for select in page.locator('select').all():
                    for i in range(select.locator('option').count()):
                        select.select_option(index=i)
                        states += 1
                for slider in page.locator('input[type=range]').all():
                    for attr in ['min', 'max']:
                        slider.evaluate('(e,a)=>{e.value=e.getAttribute(a);e.dispatchEvent(new Event("input",{bubbles:true}));}', attr)
                        states += 1
                for check in page.locator('input[type=checkbox]').all():
                    check.click()
                    states += 1
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (slug,width,'after controls')
                assert page.locator('a[href^="#"]').evaluate_all('(a)=>a.every(x=>document.getElementById(x.hash.slice(1)))')
                for href in page.locator('a[href]').evaluate_all('(a)=>a.map(x=>x.href)'):
                    u = urlparse(href)
                    if u.scheme == 'file':
                        assert Path(unquote(u.path)).is_file(), (slug, href)
                for name in ['run.py', 'results.json', 'lab.yaml', 'README.md', 'mapping.md']:
                    assert (ROOT/'papers'/slug/name).read_bytes() == (ROOT/'site/downloads'/slug/name).read_bytes()
                if width in [360,1440]:
                    page.locator('#executable_understanding').screenshot(path=f'/tmp/{slug}-{width}.png')
            page.goto((ROOT/'site/index.html').as_uri())
            for slug in SLUGS:
                assert page.locator(f'a[href="papers/{slug}.html"]').count() >= 1
            page.close()
        assert not errors, errors
        browser.close()
    print(f'PASS: 4 Labs × 4 widths; {states} control states; no JS errors; source downloads/index/links')

if __name__ == '__main__':
    main()
