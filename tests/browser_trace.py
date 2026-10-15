"""Real Chromium checks for TRACE. Serves a complete built site on localhost.

uv run --with playwright tests/browser_trace.py --site /tmp/trace-site \
    --chrome /usr/bin/chromium --screenshots /tmp/trace-browser

No model calls, external-site requests, or browser mocks. Output is a JSON
summary. Screenshots/logs should be saved outside the source repository.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from itertools import product
import json
from pathlib import Path
from threading import Thread
from urllib.parse import unquote, urlparse

from playwright.sync_api import sync_playwright

SLUG = 'trace-verifier-brittleness'
WIDTHS = [360, 390, 768, 1440]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--chrome', help='Chromium executable; otherwise Playwright default')
    parser.add_argument('--screenshots', type=Path, required=True)
    args = parser.parse_args()
    site = args.site.resolve()
    args.screenshots.mkdir(parents=True, exist_ok=True)
    results = json.loads((site / 'downloads' / SLUG / 'results.json').read_text())
    expected = results['synthetic']
    assert len(expected) == 12
    assert len(list((site / 'papers').glob('*.html'))) == 101
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(site)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    url = f'{origin}/papers/{SLUG}.html'
    errors, external_links = [], set()
    checks = local_links = 0
    try:
        with sync_playwright() as p:
            options = {'args': ['--no-sandbox', '--disable-dev-shm-usage']}
            if args.chrome:
                options['executable_path'] = args.chrome
            browser = p.chromium.launch(**options)
            version = browser.version
            for width in WIDTHS:
                page = browser.new_page(viewport={'width': width, 'height': 900})
                page.on('pageerror', lambda error: errors.append(str(error)))
                response = page.goto(url)
                assert response.status == 200
                assert '2610.11678' in page.locator('body').inner_text()
                assert '2026-08-02T05:41:14Z' in page.locator('body').inner_text()
                for a, alias, norm in product(range(3), range(2), range(2)):
                    for name, value in [('agent', a), ('alias', alias), ('normalize', norm)]:
                        page.select_option('#trace-' + name, str(value))
                    case = expected[a * 4 + alias * 2 + norm]
                    output = page.locator('#trace-output')
                    text = output.inner_text()
                    assert f'修正前 {case["raw_gap"]:.2f} → 現在 {case["gap_after"]:.2f}' in text
                    assert f'比較側の在庫：{case["changed"]["state"]["stock"]}' in text
                    assert output.locator('.trace-columns > div').nth(1).locator('li').count() == len(case['changed']['trace'])
                    output.locator('summary').click()
                    assert output.locator('details').evaluate('(x)=>x.open')
                    text = output.inner_text()
                    for record in [case['base'], case['changed']]:
                        assert record['canonical_hash'] in text
                        assert record['state_hash'] in text
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    page.locator('#trace-toy').screenshot(path=str(args.screenshots / f'trace-{width}-{a}{alias}{norm}.png'))
                    checks += 1
                page.click('#trace-reset')
                assert [page.input_value('#trace-' + name) for name in ['agent', 'alias', 'normalize']] == ['0', '1', '0']
                page.locator('#trace-normalize').focus()
                page.keyboard.press('ArrowDown')
                page.keyboard.press('Enter')
                assert page.input_value('#trace-normalize') == '1'
                assert '現在 0.00' in page.locator('#trace-output').inner_text()
                assert page.locator('a[href^="#"]').evaluate_all('(aa)=>aa.every(a=>document.getElementById(a.hash.slice(1)))')
                for href in page.locator('a[href]').evaluate_all('(aa)=>aa.map(a=>a.href)'):
                    parsed = urlparse(href)
                    if href.startswith(origin):
                        path = site / unquote(parsed.path).lstrip('/')
                        assert path.is_file(), href
                        assert page.request.get(href).status == 200, href
                        local_links += 1
                    elif parsed.scheme in ['http', 'https']:
                        external_links.add(href)
                assert page.locator('img').evaluate_all('(images)=>images.every(i=>i.complete && i.naturalWidth>0)')
                page.close()
            page = browser.new_page(java_script_enabled=False, viewport={'width': 390, 'height': 900})
            page.goto(url)
            assert '0.50' in page.locator('#trace-output').inner_text()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    assert not errors, errors
    print(json.dumps({'browser': version, 'widths': WIDTHS, 'conditions': checks,
                      'pages': 101, 'local_link_checks': local_links, 'javascript_errors': errors,
                      'keyboard_reset_no_js': 'passed', 'external_links_not_fetched': sorted(external_links)},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
