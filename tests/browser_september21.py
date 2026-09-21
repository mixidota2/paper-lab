"""Browser checks for six paper-shaped Labs at phone/tablet/desktop widths."""
from pathlib import Path
from urllib.parse import urlparse,unquote
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['lige-gr-meta-listwise','sona-yandex-music','uvr-wolt-trial-reorder','pushdualgen-kuaishou','snaplgr-snapchat','sidscope-diagnostics']
def main():
 errors=[];frames_checked=0
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/opt/google/chrome/chrome',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in [360,390,768,1440]:
   page=browser.new_page(viewport={'width':width,'height':900});page.on('pageerror',lambda e:errors.append(str(e)))
   for slug in SLUGS:
    page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(slug,width,'overflow')
    assert page.locator('figure.teaching').count()>=3,(slug,'figures')
    assert page.locator('.note-section').count()==12
    assert page.locator('a[href^="#"]').evaluate_all('(a)=>a.every(x=>document.getElementById(x.hash.slice(1)))')
    for href in page.locator('a[href]').evaluate_all('(a)=>a.map(x=>x.href)'):
     u=urlparse(href)
     if u.scheme=='file':assert Path(unquote(u.path)).is_file(),(slug,href)
    for widget in page.locator('[data-b21]').all():
     frames=json.loads(widget.locator('[data-frames]').text_content())
     for i,frame in enumerate(frames):
      widget.locator('select').select_option(str(i))
      assert widget.locator('[data-output]').inner_html()==frame
      assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(slug,width,i)
      frames_checked+=1
     widget.locator('select').focus();widget.locator('select').press('Home');widget.locator('select').press('ArrowDown');widget.locator('select').press('Enter')
     assert widget.locator('select').input_value()=='1'
     widget.locator('select').select_option('0')
    for name in ['run.py','results.json','lab.yaml','README.md','method.md','mapping.md']:
     assert (ROOT/'papers'/slug/name).read_bytes()==(ROOT/'site/downloads'/slug/name).read_bytes()
    if width in [360,1440]:
     page.screenshot(path=f'/tmp/research-2026-09-21/{slug}-{width}.png',full_page=True)
     page.locator('figure.teaching').first.screenshot(path=f'/tmp/research-2026-09-21/{slug}-figure-{width}.png')
   page.goto((ROOT/'site/index.html').as_uri())
   assert page.locator('[data-paper]').count()==51
   for slug in SLUGS:assert page.locator(f'a[href="papers/{slug}.html"]').count()>=1
   page.close()
  page=browser.new_page(java_script_enabled=False,viewport={'width':360,'height':900})
  for slug in SLUGS:
   page.goto((ROOT/'site/papers'/f'{slug}.html').as_uri())
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   for output in page.locator('[data-output]').all():assert output.inner_text().strip()
  assert not errors,errors
  browser.close()
 print(f'PASS: 6 Labs × 4 widths; {frames_checked} widget states; keyboard, links, 36 downloads, index, no-JS; no page errors')
if __name__=='__main__':main()
