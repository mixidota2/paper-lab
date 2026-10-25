"""TRACE assertions for offline output checks and the existing protected runner.
No browser launch, server, permission or security configuration lives here.
"""
from html.parser import HTMLParser
from itertools import product
import json
import re


class Frame(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.text=[]; self.codes=[]; self.steps=[]; self.bars=[]
        self.code=None; self.step=None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='code': self.code=''
        if tag=='li': self.step=''
        if tag=='div' and 'width:' in attrs.get('style',''):
            self.bars.append(float(re.search(r'width:([\d.]+)%',attrs['style'])[1]))

    def handle_data(self, text):
        self.text.append(text)
        if self.code is not None: self.code+=text
        if self.step is not None: self.step+=text

    def handle_endtag(self, tag):
        if tag=='code': self.codes.append(self.code); self.code=None
        if tag=='li': self.steps.append(self.step); self.step=None


def assert_trace_frame(html, case):
    frame=Frame(html); text=''.join(frame.text)
    records=[case['base'],case['changed']]
    assert frame.steps==[f"{s['tool']}({s['argument']}) → 在庫{s['observation']}" for r in records for s in r['trace']]
    assert [c for c in frame.codes if re.fullmatch('[0-9a-f]{64}',c)]==[
        records[0]['canonical_hash'],records[1]['canonical_hash'],records[0]['state_hash'],records[1]['state_hash']]
    for key,label in [('original_score','元の実行の点数'),('raw_score','比較側・修正前の点数'),('rescored','比較側・現在の採点方式')]:
        assert f'{label} {case[key]:.2f}' in text
    assert frame.bars==[case[key]*100 for key in ['original_score','raw_score','rescored']]
    assert f"修正前 {case['raw_gap']:.2f} → 現在 {case['gap_after']:.2f}" in text
    assert f"比較側の在庫：{case['changed']['state']['stock']}（正解5）" in text
    assert '正規の操作列：'+('同じ' if case['behavior_same'] else '違う') in text
    assert '最終状態：'+('同じ' if case['state_same'] else '違う') in text
    assert '実行のやり直しはない' in text


def assert_trace_initial(page, source):
    data=json.loads(source.read_text())
    assert [page.locator('#trace-'+key).input_value() for key in ['agent','alias','normalize']]==['0','1','0']
    assert_trace_frame(page.locator('#trace-output').inner_html(),data['synthetic'][2])


def inspect_trace(page, source):
    data=json.loads(source.read_text()); cases=data['synthetic']
    assert len(cases)==12
    assert_trace_initial(page,source)
    assert '2610.11678' in page.locator('body').inner_text()
    assert '2026-08-02T05:41:14Z' in page.locator('body').inner_text()
    for a,b,n in product(range(3),range(2),range(2)):
        for key,value in zip(['agent','alias','normalize'],[a,b,n],strict=True):
            page.locator('#trace-'+key).select_option(str(value))
        output=page.locator('#trace-output')
        assert_trace_frame(output.inner_html(),cases[a*4+b*2+n])
        output.locator('summary').click()
        assert output.locator('details').evaluate('(e)=>e.open')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        bars=output.locator('div[style*="width:"]')
        for i,key in enumerate(['original_score','raw_score','rescored']):
            ratio=bars.nth(i).evaluate('(e)=>e.getBoundingClientRect().width/e.parentElement.getBoundingClientRect().width')
            assert abs(ratio-cases[a*4+b*2+n][key])<.001
    page.locator('#trace-reset').click()
    assert_trace_initial(page,source)
    # Open the native select with a trusted key, navigate, then commit selection.
    control=page.locator('#trace-normalize');control.focus()
    control.press('Space');control.press('ArrowDown');control.press('Enter')
    assert control.input_value()=='1'
    assert_trace_frame(page.locator('#trace-output').inner_html(),cases[3])
    page.locator('#trace-reset').focus();page.locator('#trace-reset').press('Enter')
    assert_trace_initial(page,source)
    assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
