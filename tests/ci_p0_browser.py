"""PR-only protected browser checks; screenshots are separate review evidence."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from protected_firefox import launch_checked_firefox
from reference_browser import local_site

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
OUT = ROOT / 'browser-review'
SLUGS = ('spotify-incremental-recommendation-causal', 'vn2-stockout-catboost',
         'zalando-sales-event-pricing-forecast-optimize')


def inspect(base):
    assert len(list((SITE / 'papers').glob('*.html'))) == 100
    OUT.mkdir(exist_ok=True)
    errors = []
    with sync_playwright() as pw:
        if os.environ.get('LAB_BROWSER') == 'firefox':
            browser = launch_checked_firefox(pw)
        else:
            browser = pw.chromium.launch(**({"channel": os.environ["CHROME_CHANNEL"]} if os.environ.get("CHROME_CHANNEL") else {"executable_path": os.environ["CHROME_PATH"]}), chromium_sandbox=True)
        for width in (360, 1440):
            page = browser.new_page(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
            page.on('pageerror', lambda error: errors.append(str(error)))
            for slug in SLUGS:
                page.goto(base + '/papers/' + slug + '.html')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                if slug.startswith('spotify'):
                    panel = page.locator('[data-interactive=explorer]')
                    slider = panel.get_by_role('slider')
                    assert slider.input_value() == '5'
                    assert slider.get_attribute('aria-valuetext') == '自然再生の上限 θ₀：0.5（確率）'
                    assert panel.locator('output').inner_text() == '0.5（確率）'
                    for key, count in [('Home', '0'), ('End', '3')]:
                        slider.focus()
                        slider.press(key)
                        assert panel.locator('.bar-label strong').nth(1).inner_text() == count
                    panel.get_by_role('button', name='初期条件に戻す', exact=True).click()
                    assert slider.get_attribute('aria-valuetext') == '自然再生の上限 θ₀：0.5（確率）'
                if slug.startswith('vn2'):
                    panel = page.locator('[data-interactive=explorer]')
                    slider = panel.get_by_role('slider')
                    slider.focus()
                    slider.press('Home')
                    row = panel.locator('.bar-row').nth(2)
                    assert row.locator('strong').inner_text() == '推定不能'
                    assert row.locator('.bar-fill').count() == 0
                    panel.locator('details > summary').click()
                    assert panel.locator('table').first.locator('tbody tr').nth(2).locator('td').inner_text() == '推定不能'
                    for _ in range(6):
                        slider.press('ArrowRight')
                    assert slider.input_value() == '6'  # cap=18, still no uncensored period
                    assert row.locator('strong').inner_text() == '推定不能'
                    slider.press('ArrowRight')
                    assert row.locator('strong').inner_text() == '18'  # cap=19
                    slider.press('Home')
                if slug.startswith('zalando'):
                    data = json.loads((ROOT / 'papers' / slug / 'results.json').read_text())
                    assert data['verification']['mechanism'] == 'PARTIAL'
                    assert all(data['checks'].values())
                page.screenshot(path=str(OUT / f'{slug}-{width}.png'), full_page=True)
                if not slug.startswith('zalando'):
                    page.locator('[data-interactive=explorer]').screenshot(path=str(OUT / f'{slug}-{width}-controls.png'))
            page.close()
        nojs = browser.new_page(java_script_enabled=False, viewport={'width': 360, 'height': 900})
        for slug in SLUGS:
            nojs.goto(base + '/papers/' + slug + '.html')
            assert nojs.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert nojs.locator('[data-fallback]:visible').count() == nojs.locator('[data-interactive]').count()
            nojs.screenshot(path=str(OUT / f'{slug}-360-nojs.png'), full_page=True)
        assert not errors, errors
        browser.close()


if __name__ == '__main__':
    with local_site(SITE) as base:
        inspect(base)
