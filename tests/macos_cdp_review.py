"""Small CDP compatibility gate, then unchanged Lab assertions on macOS Chrome."""
from review_103_evidence import ProtectionStop
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright
from macos_chrome_cdp import chrome_process, connect_checked_cdp, verify_seatbelt
from reference_browser import local_site

ROOT = Path(__file__).resolve().parents[1]


def compatibility(shots=None,on_failure=None,protection_check=None):
    with tempfile.TemporaryDirectory(prefix='paper-lab-cdp-page-') as folder:
        Path(folder, 'index.html').write_text('''<!doctype html><meta charset="utf-8">
<label>Value<input id="value" value="1"></label><button id="apply">Apply</button>
<output id="out">1</output><input type="file" id="file"><a id="save" download="probe.json">Save</a>
<script>
const field=document.getElementById('value'), output=document.getElementById('out');
const save=document.getElementById('save'), upload=document.getElementById('file');
document.getElementById('apply').onclick=()=>{output.textContent=field.value;save.href=URL.createObjectURL(new Blob([JSON.stringify({value:field.value})],{type:'application/json'}));};
upload.onchange=async()=>{output.textContent=JSON.parse(await upload.files[0].text()).value;};
</script>''')
        with local_site(folder) as base, sync_playwright() as pw:
            browser = connect_checked_cdp(pw)
            page=None
            try:
                page = browser.new_page(viewport={'width': 360, 'height': 900}, reduced_motion='reduce')
                assert page.goto(base).ok
                (protection_check or verify_seatbelt)(browser)
                page.get_by_label('Value', exact=True).fill('0.37123')
                page.get_by_role('button', name='Apply').click()
                assert page.locator('#out').inner_text() == '0.37123'
                with page.expect_download() as download:
                    page.get_by_role('link', name='Save').click()
                saved = Path(folder) / 'probe.json'
                download.value.save_as(saved)
                assert json.loads(saved.read_text()) == {'value': '0.37123'}
                saved.write_text('{"value":"restored"}')
                page.locator('#file').set_input_files(saved)
                page.wait_for_function("document.querySelector('#out').textContent === 'restored'")
                assert page.evaluate('innerWidth') == 360
                page.set_viewport_size({'width': 1440, 'height': 900})
                assert page.evaluate('innerWidth') == 1440
                shots = Path(shots) if shots is not None else ROOT / 'browser-review' / 'compatibility'
                shots.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(shots / 'macos-chrome-cdp.png'))
                (protection_check or verify_seatbelt)(browser)
                page.close()
                print('PASS: macOS Chrome CDP HTTP/input/download/upload/viewport/screenshot compatibility', flush=True)
            except ProtectionStop:
                raise
            except Exception as error:
                if on_failure is not None:on_failure(page,error)
                raise
            finally:
                browser.close()


def main():
    with chrome_process() as (endpoint, pid):
        os.environ.update(LAB_CDP_URL=endpoint, LAB_CHROME_PID=str(pid), LAB_BROWSER='macos-cdp')
        compatibility()
        for script in ('browser.py', 'ci_p0_browser.py', 'reference_browser.py'):
            print('RUN unchanged assertions:', script, flush=True)
            subprocess.run([sys.executable, str(ROOT / 'tests' / script)], cwd=ROOT,
                           check=True, timeout=300)
            print('PASS:', script, flush=True)


if __name__ == '__main__':
    main()
