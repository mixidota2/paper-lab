"""Paper-specific figures, navigation and downloadable sources at four widths."""
import json
from pathlib import Path
from urllib.parse import urlparse,unquote
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['varg-tmall-value-generative-retrieval','accuracy-not-service-intermittent-demand','aura-disney-agentic-rec-diagnosis','grace-meta-ads-gtm-serving','icegr-baidu-intent-generative-retrieval','evopilot-verify-dont-trust-autoresearch','sidinspector-mapping-diagnostics']
def main():
 slugs=[s for s in SLUGS if (ROOT/'papers'/s/'lab.yaml').exists()]
 errors=[];states=0
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/opt/google/chrome/chrome',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in [360,390,768,1440]:
   page=browser.new_page(viewport={'width':width,'height':900});page.on('pageerror',lambda e:errors.append(str(e)))
   for s in slugs:
    page.goto((ROOT/'site/papers'/f'{s}.html').as_uri())
    page.locator('img').evaluate_all('(imgs)=>Promise.all(imgs.map(i=>{i.loading="eager";return i.decode()}))')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(s,width)
    assert page.locator('.note-section').count()==12
    assert page.locator('figure').count()>=3
    assert page.locator('a[href^="#"]').evaluate_all('(a)=>a.every(x=>document.getElementById(x.hash.slice(1)))')
    for href in page.locator('a[href]').evaluate_all('(a)=>a.map(x=>x.href)'):
     u=urlparse(href)
     if u.scheme=='file':assert Path(unquote(u.path)).is_file(),(s,href)
    for w in page.locator('[data-b21]').all():
     frames=json.loads(w.locator('[data-frames]').text_content())
     for i,frame in enumerate(frames):
      w.locator('select').select_option(str(i));assert w.locator('[data-output]').inner_html()==page.evaluate('(s)=>{const d=document.createElement("div");d.innerHTML=s;return d.innerHTML}',frame);states+=1
      assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
     w.locator('select').focus();w.locator('select').press('Home');w.locator('select').press('ArrowDown');w.locator('select').press('Enter')
     assert w.locator('select').input_value()=='1'
    for name in ['run.py','results.json','lab.yaml','README.md','method.md','mapping.md']:
     assert (ROOT/'papers'/s/name).read_bytes()==(ROOT/'site/downloads'/s/name).read_bytes()
    if width in [360,1440]:
     page.screenshot(path=f'/tmp/research-2026-09-22/{s}-{width}.png',full_page=True)
     page.locator('figure').first.screenshot(path=f'/tmp/research-2026-09-22/{s}-figure-{width}.png')
   page.goto((ROOT/'site/index.html').as_uri())
   for s in slugs:assert page.locator(f'a[href="papers/{s}.html"]').count()>=1
   page.close()
  page=browser.new_page(java_script_enabled=False,viewport={'width':360,'height':900})
  for s in slugs:
   page.goto((ROOT/'site/papers'/f'{s}.html').as_uri());assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   for o in page.locator('[data-output]').all():assert o.inner_text().strip()
  assert not errors,errors
  browser.close()
 print(f'PASS {len(slugs)} Labs × 4 widths; {states} states; keyboard, anchors, links, downloads, index, no-JS')
if __name__=='__main__':main()
