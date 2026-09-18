"""Responsive, accessible select controls, local links and source download checks."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import json, os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SLUGS=['ogr-once-generated-ranked','dream-taobao-agentic-control','pilot-experiment-lifecycle']

def main():
    errors=[]; checked=0
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROME_PATH','/opt/google/chrome/chrome'),args=['--no-sandbox','--disable-dev-shm-usage'])
        for width in [360,390,768,1440]:
            page=browser.new_page(viewport={'width':width,'height':900})
            page.on('pageerror',lambda e:errors.append(str(e)))
            for slug in SLUGS:
                page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(slug,width)
                assert page.locator('figure.teaching').count()>=4
                assert page.locator('a[href^="#"]').evaluate_all('(a)=>a.every(x=>document.getElementById(x.hash.slice(1)))')
                for href in page.locator('a[href]').evaluate_all('(a)=>a.map(x=>x.href)'):
                    u=urlparse(href)
                    if u.scheme=='file':assert Path(unquote(u.path)).is_file(),(slug,href)
                for widget in page.locator('[data-b18]').all():
                    frames=json.loads(widget.locator('[data-frames]').text_content())
                    select=widget.locator('select')
                    for i,frame in enumerate(frames):
                        select.select_option(str(i))
                        assert widget.locator('[data-output]').inner_html()==frame
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                        if widget.get_attribute('data-b18')=='schedule':
                            # Actual line boxes detect per-character wrapping and clipping.
                            assert widget.locator('th,td').evaluate_all("""cells => cells.every(cell => {
                                const range=document.createRange(); range.selectNodeContents(cell);
                                const rects=[...range.getClientRects()].filter(r=>r.width && r.height);
                                return new Set(rects.map(r=>Math.round(r.top))).size===1
                                    && cell.scrollWidth<=cell.clientWidth;
                            })"""), (width,i,'wrapped schedule cell')
                            assert widget.locator('.matrix-scroll').evaluate("""el => {
                                el.scrollLeft=el.scrollWidth;
                                const end=el.scrollLeft; el.scrollLeft=0;
                                return el.scrollWidth<=el.clientWidth || end>0;
                            }""")
                            if width in [360,390,1440]:
                                widget.locator('..').screenshot(path=f'/tmp/fixed18-schedule-{width}-{i}.png')
                        checked+=1
                    select.focus();select.press('Home');select.press('ArrowDown');select.press('Enter')
                    assert select.input_value()=='1'
                    assert widget.locator('[data-output]').inner_html()==frames[1]
                    select.select_option('0')
                # Latin tokens in the other new wide tables stay intact too.
                assert page.locator('.batch18 .matrix-scroll th, .batch18 .matrix-scroll td').evaluate_all(r"""cells => cells.every(cell => {
                    const node=cell.firstChild;
                    if (!node || node.nodeType!==Node.TEXT_NODE) return true;
                    return [...node.textContent.matchAll(/[A-Za-z0-9]+/g)].every(m=>{
                        const r=document.createRange(); r.setStart(node,m.index); r.setEnd(node,m.index+m[0].length);
                        return new Set([...r.getClientRects()].map(x=>Math.round(x.top))).size<=1;
                    });
                })"""), (slug,width,'split table token')
                for name in ['run.py','results.json','lab.yaml','README.md','method.md','mapping.md']:
                    assert (ROOT/'papers'/slug/name).read_bytes()==(ROOT/'site/downloads'/slug/name).read_bytes()
                if width in [360,1440]:page.screenshot(path=f'/tmp/{slug}-{width}-18.png',full_page=True)
            page.goto((ROOT/'site/index.html').as_uri())
            assert page.locator('[data-paper]').count()==45
            for slug in SLUGS:assert page.locator(f'a[href="papers/{slug}.html"]').count()>=1
            page.close()
        page=browser.new_page(java_script_enabled=False,viewport={'width':360,'height':900})
        for slug in SLUGS:
            page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for output in page.locator('[data-output]').all():assert output.inner_text().strip()
        assert not errors,errors
        browser.close()
    print(f'PASS: 3 Labs x 360/390/768/1440; {checked} selected frames; keyboard, links, 18 downloads, index, no-JS; no page errors')

if __name__=='__main__':main()
