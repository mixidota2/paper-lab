"""Assertions within the existing guarded browser; no launcher or external IO."""
import json


def assert_arc_dom(actual, case, stage):
    s=case['stages'][stage]
    assert actual['stage']==str(stage)
    assert actual['stageGate']==('PASS' if s['gate'] else 'FAIL')
    suites=[('自己テスト',s['self_test']),('stage F2P',s['f2p']),('stage P2P',s['p2p'])]
    if stage==2:
        suites += [('chain F2P',case['chain']['f2p']),('chain P2P',case['chain']['p2p'])]
        assert actual['chainGate']==('PASS' if case['chain']['gate'] else 'FAIL')
    else:
        assert actual['chainGate'] is None and actual['pending']
    assert len(actual['suites'])==len(suites)
    for got,(label,expected) in zip(actual['suites'],suites):
        assert got['label']==label
        assert got['gate']==('PASS' if expected['passed'] else 'FAIL')
        assert len(got['checks'])==len(expected['checks'])
        expectation='自己テストの期待値' if label=='自己テスト' else '仕様の期待値'
        other='仕様の期待値' if label=='自己テスト' else '自己テストの期待値'
        for text,c in zip(got['checks'],expected['checks']):
            compact=lambda value:json.dumps(value,ensure_ascii=False,separators=(',',':'))
            assert c['name']+'：'+('PASS' if c['passed'] else 'FAIL') in text
            assert f"{c['op']}({compact(c['values'])}, 閾値 {c['threshold']}, 上限 {c['limit']})" in text
            assert other not in text
            assert f"{expectation} {compact(c['expected'])} ／ 実際 {compact(c['actual'])}" in text
    for item in actual['geometry']:
        left,top,right,bottom=item['box']
        assert right>left and bottom>top
        for x0,y0,x1,y1 in item['text']:
            assert left-1<=x0<=x1<=right+1, 'FeatureArc text crosses card boundary'
            assert top-1<=y0<=y1<=bottom+1, 'FeatureArc text crosses row boundary'


DOM = r"""()=>{
 const root=document.getElementById('arc-output');
 const geometry=[...root.querySelectorAll('.arc-check')].map(e=>{
  const b=e.getBoundingClientRect(),w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT),text=[];
  while(w.nextNode()){if(!w.currentNode.textContent.trim())continue;
   const r=document.createRange();r.selectNodeContents(w.currentNode);
   for(const b of r.getClientRects())text.push([b.left,b.top,b.right,b.bottom]);}
  return {box:[b.left,b.top,b.right,b.bottom],text};
 });
 return {stage:root.querySelector('[data-stage]').dataset.stage,
  stageGate:root.querySelector('[data-stage-gate]').textContent,
  chainGate:root.querySelector('[data-chain-gate]')?.textContent??null,
  pending:!!root.querySelector('[data-chain-pending]'),geometry,
  suites:[...root.querySelectorAll('.arc-suite')].map(e=>({label:e.querySelector('[data-gate]').dataset.gate,
   gate:e.querySelector('[data-gate]').textContent,checks:[...e.querySelectorAll('.arc-check')].map(x=>x.innerText)}))};
}"""


def inspect_featurearc(page, source, capture):
    cases=json.loads(source.read_text())['synthetic']
    for c in cases:
        page.locator('#arc-reset').click()
        page.locator('#arc-scenario').select_option(c['scenario'])
        page.locator('#arc-repair').set_checked(c['repair'])
        for stage in range(3):
            if stage:
                button=page.locator('#arc-next');button.focus()
                assert button.evaluate('e=>e===document.activeElement')
                button.press('Enter')
            assert_arc_dom(page.evaluate(DOM),c,stage)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert page.locator('#arc-next').is_disabled()
        if c['scenario']=='inherited':capture('repair' if c['repair'] else 'inherited')
        if c['scenario']=='oracle' and not c['repair']:
            page.locator('#arc-prev').click();page.locator('#arc-prev').click()
            assert_arc_dom(page.evaluate(DOM),c,0)
            capture('oracle')
    reset=page.locator('#arc-reset');reset.focus();reset.press('Enter')
    assert page.locator('#arc-scenario').input_value()=='inherited'
    assert not page.locator('#arc-repair').is_checked()
    assert page.locator('#arc-prev').is_disabled()
    assert_arc_dom(page.evaluate(DOM),cases[0],0)
