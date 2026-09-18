"""Responsive, interactive, navigation and download checks for September 17."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SLUGS=['genpage-netflix-homepage','unirec-chain-of-attribute','agentx-kuaishou','static-constrained-gr','flashtrie-gpu-beam','gatesid-coldstart-ranking','coral-meta-config-harness']

def main():
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROME_PATH','/opt/google/chrome/chrome'),args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in [360,768,1440]:
            page=browser.new_page(viewport={'width':width,'height':900})
            page.on('pageerror',lambda e:errors.append(str(e)))
            for slug in SLUGS:
                path=ROOT/'site/papers'/f'{slug}.html'
                page.goto(path.as_uri())
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(slug,width)
                assert page.locator('figure.teaching').count()>=3
                assert page.locator('a[href^="#"]').evaluate_all('(a)=>a.every(x=>document.getElementById(x.hash.slice(1)))')
                for href in page.locator('a[href]').evaluate_all('(a)=>a.map(x=>x.href)'):
                    u=urlparse(href)
                    if u.scheme=='file':assert Path(unquote(u.path)).is_file(),(slug,href)
                for name in ['run.py','results.json','README.md','lab.yaml','method.md','mapping.md']:
                    source=ROOT/'papers'/slug/name
                    copy=ROOT/'site/downloads'/slug/name
                    assert copy.read_bytes()==source.read_bytes()
                if slug=='flashtrie-gpu-beam':
                    control=page.locator('[data-b17=slo] select')
                    control.select_option('1')
                    assert 'BWは200' in page.locator('[data-b17=slo] [data-output]').inner_text()
                    control.select_option('4')
                    assert 'BWは1000' in page.locator('[data-b17=slo] [data-output]').inner_text()
                if slug=='gatesid-coldstart-ranking':
                    control=page.locator('[data-b17=gate] input')
                    control.focus();control.press('Home')
                    assert 'w=0：' in page.locator('[data-b17=gate] [data-output]').inner_text()
                    control.press('End')
                    assert 'w=1：' in page.locator('[data-b17=gate] [data-output]').inner_text()
                if width in [360,1440]:
                    page.screenshot(path=f'/tmp/{slug}-{width}-17.png',full_page=True)
            page.goto((ROOT/'site/index.html').as_uri())
            assert page.locator('[data-paper]').count()==len(list((ROOT/'papers').glob('*/lab.yaml')))
            for slug in SLUGS:
                assert page.locator(f'a[href="papers/{slug}.html"]').count()>=1
            page.close()
        page=browser.new_page(java_script_enabled=False,viewport={'width':360,'height':900})
        for slug in SLUGS:
            page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('figure.teaching').count()>=3
            for node in page.locator('[data-b17] [data-output]').all():assert node.inner_text().strip()
        assert not errors,errors
        browser.close()
    print('PASS: 7 Labs × 360/768/1440; controls, links, 42 downloads, index, no-JS; no page errors')

if __name__=='__main__':main()
