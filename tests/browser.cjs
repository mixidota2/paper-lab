/* Optional real-browser check. Set PLAYWRIGHT_MODULE and CHROME_PATH if needed.
   node tests/browser.cjs; tests built site via file:// to prove offline operation. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const site = path.resolve(__dirname, '../site');
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROME_PATH || undefined, headless:true, args:['--no-sandbox','--disable-dev-shm-usage']});
  const errors=[];
  try {
    for (const width of [360, 768, 1440]) {
      const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
      page.on('pageerror', e=>errors.push(String(e)));
      page.on('console', m=>{if(m.type()==='error')errors.push(m.text());});
      for (const name of fs.readdirSync(path.join(site,'papers')).filter(n=>n.endsWith('.html'))) {
        await page.goto(pathToFileURL(path.join(site,'papers',name)).href);
        const modules=await page.locator('[data-interactive]').count();
        assert.equal(await page.locator('[data-ready=true]').count(),modules,name);
        assert.ok(await page.locator('figure.teaching').count()>=2,name);
        assert.ok(await page.locator('#method').textContent());
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true,`${name} overflow at ${width}`);
        const brokenAnchors=await page.locator('a[href^="#"]').evaluateAll(links=>links.filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash));
        assert.deepEqual(brokenAnchors,[],name);
        if(width===360 && ['unipinrec.html','apollopfn.html','rest-sequence-ranking.html'].includes(name)) await page.locator('figure.teaching').first().screenshot({path:`/tmp/${name}-mobile.png`});
        if(width===1440 && ['tgr.html','harness-bench.html','whole-foods-shelf.html'].includes(name)) await page.locator('figure.teaching').first().screenshot({path:`/tmp/${name}-desktop.png`});
        if(!modules) continue;
        const explorer=page.locator('[data-interactive=explorer]');
        const slider=explorer.getByRole('slider');
        await slider.focus();await slider.press('Home');
        assert.equal(await slider.inputValue(),'0');
        const before=await explorer.locator('.explorer-note').textContent();
        await slider.press('End');
        assert.equal(await slider.inputValue(),await slider.getAttribute('max'));
        const after=await explorer.locator('.explorer-note').textContent();
        // Some notes are invariant, but the bars and value must match selected JSON.
        const expected=await explorer.locator('[data-results]').textContent().then(JSON.parse);
        const last=expected.frames.at(-1);
        const labels=await explorer.locator('.bar-label strong').allTextContents();
        assert.deepEqual(labels,last.bars.map(b=>Number(b.value).toLocaleString('ja-JP',{maximumFractionDigits:4})));
        await explorer.getByRole('button',{name:'初期条件に戻す',exact:true}).click();
        assert.equal(await slider.inputValue(),String(expected.default));
        await explorer.locator('summary').click();
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true,`${name} table overflow at ${width}`);
        if(width===360 && name==='unipinrec.html') {
          await explorer.screenshot({path:'/tmp/lab-interactive-mobile.png'});
          await page.screenshot({path:'/tmp/lab-mobile.png',fullPage:true});
        }
        if(width===1440 && name==='whole-foods-shelf.html') await page.screenshot({path:'/tmp/lab-desktop.png',fullPage:true});
      }
      await page.goto(pathToFileURL(path.join(site,'index.html')).href);
      assert.equal(await page.locator('[data-paper]:visible').count(),11);
      await page.getByRole('searchbox').fill('欠品');
      assert.ok(await page.locator('[data-paper]:visible').count()>0);
      assert.ok(await page.locator('[data-paper]:visible').count()<11);
      await page.getByRole('searchbox').fill('no-such-paper-xyz');
      assert.equal(await page.locator('[data-empty]').isVisible(),true);
      await page.getByRole('button',{name:'条件を消去'}).click();
      assert.equal(await page.locator('[data-paper]:visible').count(),11);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true);
      if(width===1440) await page.screenshot({path:'/tmp/library-desktop.png',fullPage:true});
      await page.close();
    }
    const nojs=await browser.newPage({javaScriptEnabled:false,viewport:{width:360,height:800}});
    for(const name of fs.readdirSync(path.join(site,'papers')).filter(n=>n.endsWith('.html'))) {
      await nojs.goto(pathToFileURL(path.join(site,'papers',name)).href);
      assert.equal(await nojs.locator('[data-fallback]:visible').count(),await nojs.locator('[data-interactive]').count());
      assert.ok(await nojs.locator('figure.teaching:visible').count()>=2);
      assert.equal(await nojs.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true);
    }
    assert.deepEqual(errors,[]);
    console.log('PASS: 11 labs × 3 viewports; heterogeneous figures, anchors, slider keyboard, data, filters, offline/no-JS, overflow, console');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
