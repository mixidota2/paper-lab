"""Survey content contracts and actual filter JS; no corporate-effect reproduction."""
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import yaml
import pytest
from paper_lab.build import build
from paper_lab.replenishment_guide import load_cards, render_cards, FIELDS

ROOT=Path(__file__).resolve().parents[1]
GUIDES=ROOT/'guides'
SOURCE=GUIDES/'replenishment-evidence.yaml'
BASE='512b8bc14b7f8e477e604c5a5fc24fc9233d270d'

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__();self.tags=[];self.text=[];self.feed(text)
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
    def handle_data(self,data):self.text.append(data)


def test_reviewed_source_contract_dates_scopes_and_units():
    data=load_cards(SOURCE);cards={c['id']:c for c in data['cards']}
    assert data['checked']=='2026-11-02' and data['period_start']=='2025-11-01' and data['period_end']=='2026-11-30'
    assert [(c['id'],c['publication_date'],c['evaluation'],c['period']) for c in data['cards']]==[
        ('zalando','2026-01-15','backtest','current'),('jd-orpr','2025-12-22','observational','current'),
        ('amazon-rme','2026-09-11','model','current'),('alibaba','2023-09-26','observational','legacy'),
        ('jd-e2e','2022-12-13','observational','legacy')]
    expected={
        'zalando':{'result':['GMV +22.11%','+21.95%','全提案採用の仮想結果','本番A/Bではない'],
                   'forecast':['分位点','検閲補正式は未確認'],'scope':['200万article','800販売者'],
                   'limitation':['2025-12-19','2026-01-30','本文は未取得']},
        'jd-orpr':{'result':['−5.27日','+2.29%（単位は原文表記）','−29.95%','−4.07日','+0.47%','−18.35パーセントポイント'],
                   'scope':['331 SKU','3,899 SKU–DC','無作為化ではない'],'limitation':['反実仮想欠品損失は評価外']},
        'amazon-rme':{'task':['保全','店舗販売商品の補充とは対象が異なる'],
                      'result':['モデル上の節約額が30.5%改善','実際の総費用30.5%削減ではない','週の割合','99.8%'],
                      'limitation':['10.1080/00207543.2026.2655026','別研究','読了・同一性を主張しない']},
        'alibaba':{'result':['−37.45%','1.3% reduction','相対%かパーセントポイントか断定しない'],
                   'scope':['40,000 SKU×倉庫','低回転','販促祭前に停止'],'operation':['無作為化A/Bではない']},
        'jd-e2e':{'task':['教師ありE2E','RLではない'],'result':['−40.4%','−637.24評価費用単位','会計利益ではない'],
                  'scope':['9,308 SKU','12 DC','自主参加','無作為化ではない'],'limitation':['最終版との全文照合は未完']}}
    for key,fields in expected.items():
        for field,phrases in fields.items():
            assert all(p in cards[key][field] for p in phrases),(key,field)
    assert cards['amazon-rme']['domain']=='maintenance'
    for card in cards.values():
        assert '未確認' in card['forecast']
        assert all(card[field] for field in FIELDS)
    text=(GUIDES/'forecast-to-replenishment.md').read_text()
    # Financial quantities live only in the evidence cards, not duplicate comparison tables.
    for token in ['22.11','21.95','5.27','18.35','30.5','37.45','637.24','40.4']:
        assert token not in text
    for phrase in ['採用企業全体の導入率は推定できず','本ガイドの分析・提案','手法別の導入率も不明','相対%とパーセントポイント',
                   '同じ潜在需要・納期・返品、初期在庫・未着注文','平行トレンド','fill rate','cycle service level',
                   '強い基準','需要上下限','学習・調整・最終評価','シャドー運用','全原典を再取得・再読したものではない']:
        assert phrase in text
    assert '百分点' not in SOURCE.read_text()+text


@pytest.mark.parametrize('mutation',['date','period','evaluation','missing-field','duplicate-id','unsafe-url','missing-source'])
def test_invalid_evidence_rejected(tmp_path,mutation):
    d=copy.deepcopy(load_cards(SOURCE));c=d['cards'][0]
    if mutation=='date':c['publication_date']='2027-01-01'
    if mutation=='period':c['period']='legacy'
    if mutation=='evaluation':c['evaluation']='randomized-ab'
    if mutation=='missing-field':del c['forecast']
    if mutation=='duplicate-id':d['cards'][1]['id']=c['id']
    if mutation=='unsafe-url':c['sources'][0]['url']='javascript:alert(1)'
    if mutation=='missing-source':c['sources']=[]
    p=tmp_path/'cards.yaml';p.write_text(yaml.safe_dump(d,allow_unicode=True))
    with pytest.raises(ValueError):load_cards(p)


def test_cards_are_rendered_once_with_sources_and_escaped_fields():
    d=load_cards(SOURCE);html=render_cards(d);doc=Document(html)
    articles=[a for t,a in doc.tags if t=='article']
    assert [a['id'] for a in articles]==['case-'+c['id'] for c in d['cards']]
    assert len(articles)==5 and all('hidden' not in a for a in articles)
    text=''.join(doc.text)
    for c in d['cards']:
        for field in FIELDS:assert text.count(c[field])==1
        for s in c['sources']:assert any(t=='a' and a.get('href')==s['url'] for t,a in doc.tags)
    assert '<noscript>' in html
    d['cards'][0]['task']='<img src=x onerror=alert(1)>'
    escaped=render_cards(d)
    assert '<img src=x' not in escaped and '&lt;img' in escaped


def test_actual_filter_js_all_combinations_events_reset_and_no_matches(tmp_path):
    data=load_cards(SOURCE)
    payload=tmp_path/'cards.json';payload.write_text(json.dumps(data))
    script=tmp_path/'check.cjs'
    script.write_text(r'''
const assert=require('node:assert/strict'),fs=require('fs');
const ui=require(process.argv[2]),data=JSON.parse(fs.readFileSync(process.argv[3]));
const cards=data.cards.map(c=>({dataset:{period:c.period,domain:c.domain,evaluation:c.evaluation},hidden:false}));
const groups=['current','legacy'].map(p=>({dataset:{cardGroup:p},hidden:false}));
const node=value=>({value,hidden:false,textContent:'',events:{},addEventListener(k,fn){this.events[k]=fn;}});
const controls={period:node('all'),domain:node('all'),evaluation:node('all')},count=node(),empty=node(),reset=node();
const root={querySelectorAll(q){if(q==='[data-evidence-card]')return cards;if(q==='[data-card-group]')return groups;throw Error(q);},
 querySelector(q){const m=q.match(/^\[data-filter="(\w+)"\]$/);if(m)return controls[m[1]];return {'[data-filter-count]':count,'[data-filter-empty]':empty,'[data-filter-reset]':reset}[q];}};
ui.mount(root);let combinations=0;
for(const period of ['all','current','legacy'])for(const domain of ['all','retail','maintenance'])for(const evaluation of ['all','backtest','model','observational']){
 const state={period,domain,evaluation};for(const k of Object.keys(state))controls[k].value=state[k];
 controls.evaluation.events.change();
 const expected=data.cards.map(c=>(period==='all'||c.period===period)&&(domain==='all'||c.domain===domain)&&(evaluation==='all'||c.evaluation===evaluation));
 assert.deepEqual(cards.map(c=>!c.hidden),expected);assert.equal(count.textContent,`${expected.filter(Boolean).length}件 / 全5件`);
 assert.equal(empty.hidden,expected.some(Boolean));
 for(const g of groups)assert.equal(g.hidden,!data.cards.some((c,i)=>c.period===g.dataset.cardGroup&&expected[i]));
 combinations++;
}
assert.equal(combinations,36);
// Last state legacy/maintenance/observational is empty; reset must reveal all cards.
assert(cards.every(c=>c.hidden));reset.events.click();assert(cards.every(c=>!c.hidden));
assert.deepEqual(Object.fromEntries(Object.entries(controls).map(([k,c])=>[k,c.value])),ui.defaults());
assert.throws(()=>ui.matches(cards[0].dataset,{...ui.defaults(),evaluation:'randomized-ab'}));
for(const control of Object.values(controls))assert.equal(typeof control.events.change,'function');
console.log('36 combinations, native-handler wiring, empty state and reset PASS (mock DOM, not browser)');
''')
    r=subprocess.run(['node',str(script),str(GUIDES/'replenishment-filter.js'),str(payload)],capture_output=True,text=True,check=True)
    assert '36 combinations' in r.stdout


def test_full_build_guide_sources_links_and_existing_labs_preserved(tmp_path):
    site=tmp_path/'site';labs=build(root=ROOT,site_dir=site)
    assert len(labs)==109
    from review_103 import preflight
    p=preflight(site)
    assert p['theme_guides']==2 and p['guide_pages']==3 and len(p['required_cases'])==423
    target=site/'guides/forecast-to-replenishment.html';text=target.read_text();doc=Document(text)
    assert sum(t=='article' and 'data-evidence-card' in a for t,a in doc.tags)==5
    assert '<!-- EVIDENCE_CARDS -->' not in text
    for name in ['forecast-to-replenishment.md','replenishment-evidence.yaml']:
        assert (site/'downloads/guides'/name).read_bytes()==(GUIDES/name).read_bytes()
    assert (site/'assets/replenishment-filter.js').read_bytes()==(GUIDES/'replenishment-filter.js').read_bytes()
    assert 'forecast-to-replenishment.html' in (site/'guides/index.html').read_text()
    assert '2件のテーマガイド' in (site/'guides/shelf-decisions.html').read_text()
    expected=render_cards(load_cards(SOURCE))
    assert expected in text
    # Preserve the completed inventory Lab and every other paper plus the original guide source.
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'papers','guides/shelf-decisions.md'],cwd=ROOT,text=True).splitlines()
    for path in paths:
        before=subprocess.check_output(['git','rev-parse',f'{BASE}:{path}'],cwd=ROOT,text=True).strip()
        after=subprocess.check_output(['git','hash-object',path],cwd=ROOT,text=True).strip()
        # Explicit CDF portability repair: exact blob identities, all other source unchanged.
        portability_repair = {'papers/inventory-common-threshold-history/run.py': 'e0bd34bd4ac3b2139c3b6064f0dfc75e41a5d2e6', 'papers/inventory-common-threshold-history/README.md': '73d49ee6ab6ea7e3fbb790397cf58ffafd2561e3', 'papers/inventory-common-threshold-history/results.json': '4e7459bc5e8fbd88da253ba91afa77db2a7b8cb9'}
        assert after==portability_repair.get(path,before),path
