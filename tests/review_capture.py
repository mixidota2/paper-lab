"""Capture actual viewport tiles, never a renderer-sized full-page surface."""
import base64
import json
import hashlib
import struct


def capture_segments(page, path):
    path = path.with_suffix('')
    path.mkdir(parents=True, exist_ok=True)
    print('CAPTURE START', path.name, flush=True)
    # Do not await page callbacks: script-disabled documents cannot dispatch them.
    # Native loading still works; poll it synchronously from the test process.
    page.evaluate("() => { for (const img of document.images) img.loading='eager'; }")
    for _ in range(100):
        ready = page.evaluate("document.fonts.status === 'loaded' && [...document.images].every(i => i.complete && i.naturalWidth > 0)")
        if ready:
            break
        page.wait_for_timeout(100)
    assert ready, 'Fonts/images did not finish loading within 10 seconds'
    bounds = page.evaluate('''() => {
      const d=document.documentElement, bad=[]; let count=0, right=0;
      for (const root of document.querySelectorAll('.prose, .footer')) {
        const walk=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
        while(walk.nextNode()) {
          const n=walk.currentNode;
          if(!n.textContent.trim() || n.parentElement.closest('table, pre, svg, script, style')) continue;
          const r=document.createRange(); r.selectNodeContents(n);
          for(const box of r.getClientRects()) {
            if(!box.width || !box.height) continue;
            count++; right=Math.max(right,box.right);
            if(box.left < -1 || box.right>d.clientWidth+1) bad.push({text:n.textContent.slice(0,60),left:box.left,right:box.right});
          }
        }
      }
      return {innerWidth,clientWidth:d.clientWidth,scrollWidth:d.scrollWidth,height:d.scrollHeight,viewportHeight:innerHeight,textRects:count,rightmostText:right,bad};
    }''')
    assert bounds['textRects'] > 0, bounds
    assert not bounds['bad'], bounds
    assert bounds['scrollWidth'] <= bounds['innerWidth'], bounds
    session = page.context.new_cdp_session(page)
    tiles=[]
    try:
        target=0
        while True:
            page.evaluate('(y) => window.scrollTo({top:y,behavior:"instant"})', target)
            page.wait_for_timeout(50)  # Test-side paint allowance; no page callback.
            m=page.evaluate('''() => ({x:scrollX,y:scrollY,width:innerWidth,height:innerHeight,total:document.documentElement.scrollHeight,clientWidth:document.documentElement.clientWidth})''')
            assert m['width']==bounds['innerWidth'] and m['clientWidth']==bounds['clientWidth'], m
            if tiles:
                assert 0 < m['y']-tiles[-1]['y'] <= m['height']-99, m
            data=session.send('Page.captureScreenshot', {'format':'png','fromSurface':True,'captureBeyondViewport':False,
                'clip':{'x':0,'y':m['y'],'width':m['width'],'height':m['height'],'scale':1}})
            png=base64.b64decode(data['data'])
            size=struct.unpack('>II',png[16:24])
            assert size==(m['width'],m['height']), (size,m)
            digest=hashlib.sha256(png).hexdigest()
            assert digest not in [t['sha256'] for t in tiles], 'Repeated viewport pixels'
            name=f'{len(tiles):03d}.png'
            (path/name).write_bytes(png)
            tiles.append(dict(m,file=name,pngWidth=size[0],pngHeight=size[1],sha256=digest))
            # scrollHeight is integral; do not stop a pixel before its end.
            if m['y']+m['height'] >= m['total']:
                break
            target=m['y']+m['height']-100
        footer=page.locator('.footer').bounding_box()
        assert footer and footer['y']>=0 and footer['y']+footer['height'] <= m['height'], footer
        assert page.locator('.footer a').is_visible()
        report=dict(bounds=bounds,tiles=tiles,footer=footer,method='Unresized viewport; 100px or greater overlap; no stitching')
        (path/'segments.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print('CAPTURE',path.name,json.dumps(dict(bounds=bounds,tiles=len(tiles),last=tiles[-1],footer=footer)),flush=True)
    finally:
        session.detach()
        page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
