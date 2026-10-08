"""October 8: each paper's controls, provenance links, and phone/PC layouts."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SLUGS=['sim2real-policy-conditioned-inbound-forecast','harness-buys-tokens-not-pass-rate','traffic-forecast-to-decision-value','hear-harness-engine-serving-protocol']

def main():
    errors=[]
    states=0
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/opt/google/chrome/chrome',args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in [360,390,768,1440]:
            page=browser.new_page(viewport={'width':width,'height':1000})
            page.on('pageerror',lambda e:errors.append(str(e)))
            for slug in SLUGS:
                page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
                assert page.locator('.note-section').count()==12
                assert page.locator('.b08').count()==1
                Path('/tmp/lint-ui-'+slug+'.md').write_text('\n\n'.join(page.locator('.b08 p').all_inner_texts()))
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(slug,width)
                if slug.startswith('sim2real'):
                    before=page.locator('[data-equation]').inner_text()
                    page.locator('[data-cost]').select_option('4')
                    assert before!=page.locator('[data-equation]').inner_text()
                elif slug.startswith('harness-buys'):
                    page.locator('[data-n]').select_option('45')
                    assert '到達不可' in page.locator('[data-power]').inner_text()
                    page.locator('[data-papersteps]').uncheck()
                    page.locator('[data-steps]').fill('200')
                    page.locator('[data-steps]').dispatch_event('input')
                    before=page.locator('[data-bill]').inner_text()
                    page.locator('[data-compact]').check()
                    assert before!=page.locator('[data-bill]').inner_text()
                elif slug.startswith('traffic'):
                    assert '価値ゼロ' in page.locator('[data-oracle]').inner_text()
                    page.locator('[data-actions]').select_option('several')
                    assert '正の価値' in page.locator('[data-oracle]').inner_text()
                    for button in page.locator('[data-gate]').all():button.click();states+=1
                else:
                    for _ in range(4):page.locator('[data-next]').click();states+=1
                    assert page.locator('[data-next]').is_disabled()
                    page.locator('[data-reset]').click()
                    for k in ['fcfs','cache','cache_guard']:
                        page.locator(f'[data-policy="{k}"]').last.click();states+=1
                for select in page.locator('.b08 select').all():
                    for i in range(select.locator('option').count()):select.select_option(index=i);states+=1
                for slider in page.locator('.b08 input[type=range]').all():
                    for attr in ['min','max']:
                        slider.evaluate('(e,a)=>{e.value=e.getAttribute(a);e.dispatchEvent(new Event("input",{bubbles:true}));}',attr);states+=1
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(slug,width,'after')
                assert 'NaN' not in page.locator('.b08').inner_text()
                assert page.locator('a[href^="#"]').evaluate_all('(a)=>a.every(x=>document.getElementById(x.hash.slice(1)))')
                for href in page.locator('a[href]').evaluate_all('(a)=>a.map(x=>x.href)'):
                    u=urlparse(href)
                    if u.scheme=='file':assert Path(unquote(u.path)).is_file(),(slug,href)
                for name in ['run.py','results.json','lab.yaml','README.md','mapping.md','method.md']:
                    assert (ROOT/'papers'/slug/name).read_bytes()==(ROOT/'site/downloads'/slug/name).read_bytes()
                if width in [360,1440]:
                    page.locator('.b08').screenshot(path=f'/tmp/{slug}-{width}.png')
            page.goto((ROOT/'site/index.html').as_uri())
            for slug in SLUGS:assert page.locator(f'a[href="papers/{slug}.html"]').count()>=1
            page.close()
        browser.close()
    assert not errors,errors
    print(f'PASS: 4 Labs × 4 widths, {states} control states, links/downloads/index, no JS errors')

if __name__=='__main__':main()
