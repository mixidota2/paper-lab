"""Prepared, NOT EXECUTED here: protected browser checks for the two reference Labs.
Build all pages first. CHROME_PATH must select an already installed protected Chromium.
"""
import json
import os
from pathlib import Path
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

ROOT=Path(__file__).resolve().parents[1]
SITE=Path(os.environ.get('REFERENCE_SITE',str(ROOT/'site'))).resolve()
OUT=Path(os.environ.get('REFERENCE_SHOTS','/tmp/reference-browser-shots'))
IDS=['reasoncast-agentic-demand-forecasting','retailbench-long-horizon-store-agents']


@contextmanager
def local_site(directory):
    """Serve only the built site on loopback; stop even when assertions fail."""
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive(), 'HTTP server did not stop'


def inspect(base_url):
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ['CHROME_PATH'],chromium_sandbox=True)
        for width in (360,1440):
            page=browser.new_page(viewport={'width':width,'height':900},reduced_motion='reduce')
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('requestfailed',lambda request:errors.append(request.url+' '+str(request.failure)))
            page.on('response',lambda response:errors.append(str(response.status)+' '+response.url) if response.status>=400 else None)
            for slug in IDS:
                response=page.goto(f'{base_url}/papers/{slug}.html')
                assert response.ok and page.url.startswith(base_url+'/')
                root=page.locator('[data-reference-lab]')
                assert root.get_attribute('data-ready')=='true'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                if slug.startswith('reasoncast'):
                    assert '29.289322' in root.locator('[data-output]').inner_text()
                    field=root.locator('[name=gate]');field.focus();field.press('ControlOrMeta+A');field.press('Backspace');field.press('0');field.press('.');field.press('3');field.press('7');field.press('1');field.press('2');field.press('3')
                    expected='gate';value=.37123
                else:
                    field=root.locator('[name=return_b]');field.fill('0.13791');field.press('Tab')
                    expected='return_b';value=.13791
                with page.expect_download() as download:
                    root.get_by_role('button',name='JSONを書き出す',exact=True).click()
                saved=OUT/f'{slug}-{width}.json';download.value.save_as(saved)
                payload=json.loads(saved.read_text());assert payload['inputs'][expected]==value
                root.locator(f'[name={expected}]').fill('0.9')
                payload['output']='untrusted'
                root.locator('[data-json]').fill(json.dumps(payload))
                root.get_by_role('button',name='条件を読み込み、再計算する',exact=True).click()
                assert not root.locator('[data-error]').inner_text()
                assert root.locator(f'[name={expected}]').input_value()==str(value)
                assert 'untrusted' not in root.locator('[data-output]').inner_text()
                root.locator('[data-json]').fill('{bad json')
                root.get_by_role('button',name='条件を読み込み、再計算する',exact=True).click()
                assert '読み込み失敗' in root.locator('[data-error]').inner_text()
                root.get_by_role('button',name='初期条件に戻す',exact=True).click()
                assert not root.locator('[data-error]').inner_text()
                assert root.locator('[data-json]').input_value()==''
                assert root.locator(f'[name={expected}]').input_value()==('0.5' if expected=='gate' else '0.05')
                for line in root.locator('svg polyline').all():
                    assert not any(v in line.get_attribute('points') for v in ('NaN','Infinity'))
                box=root.locator('svg').bounding_box()
                assert box and box['width']>0 and box['height']>0
                page.screenshot(path=str(OUT/f'{slug}-{width}-default.png'),full_page=True)
                if slug.startswith('reasoncast'):
                    root.locator('[name=actual]').fill('0,0,0,0,0,0,0')
                    assert '未定義' in root.locator('[data-output]').inner_text()
                    root.locator('[name=actual]').fill('10,10,10,10,10,10,10')
                    root.locator('[name=additive]').fill('-15,-15,-15,-15,-15,-15,-15')
                    root.locator('[name=gate]').fill('1')
                    assert '負の予測' in root.locator('[data-output]').inner_text()
                    root.locator('[name=route]').select_option('Skip')
                else:
                    for key,val in dict(cash=40,demand=10,rent=35,days=2,return_a=.15,return_b=0).items():root.locator(f'[name={key}]').fill(str(val))
                    root.locator('[name=mode]').select_option('funded')
                    summary=root.locator('[data-output] table').first
                    assert summary.locator('tbody tr').nth(0).locator('td').nth(2).inner_text()=='60'
                    assert summary.locator('tbody tr').nth(1).locator('td').nth(2).inner_text()=='55'
                page.screenshot(path=str(OUT/f'{slug}-{width}.png'),full_page=True)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.close()
        assert not errors,errors
        browser.close()


def main():
    with local_site(SITE) as base_url:
        inspect(base_url)


if __name__=='__main__':main()
