"""Prepared 106-Lab review. --preflight never launches a browser; --run is explicit.
Existing macOS signed-Chrome/loopback-CDP/Seatbelt guards are mandatory.
"""
import argparse
import ast
from contextlib import contextmanager
from functools import partial
import hashlib
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from review_103_evidence import RunEvidence, ProtectionStop
from catalog_expectations import assert_catalog, WRAPPED, TRACE, EPISEM
from episem_review import inspect_episem
from trace_review import inspect_trace, assert_trace_initial
from wrapped_review import inspect_wrapped, assert_wrapped_initial
from review_measurements import assert_percent_width
import tempfile
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen, Request
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
SHELF = ['storewide-shelf-decomposition','assortment-replenishment-hard-constraints','shelf-placement-options']
EXPLORERS = ['vn2-stockout-catboost','whole-foods-shelf','contextual-deconvolution']
STATIC = ['case-against-generation-retrieval','tgr','forecast-critic','apollopfn','gr4ad-ads-generative']
DISPLAY = {
 'constrained-deep-inventory-fbsde':['data-b21'],
 'sim2real-policy-conditioned-inbound-forecast':['data-cost','data-study','data-week'],
 'harness-buys-tokens-not-pass-rate':['data-papersteps','data-compact','data-price','data-steps'],
 'traffic-forecast-to-decision-value':['data-gates','data-actions'],
 'hear-harness-engine-serving-protocol':['data-next','data-reset','data-benchmark','data-event'],
 'sabreagent-design-time-inventory':['data-b21'],
 'exaone-demand-routed-tsfm':['data-a','data-c','data-stock','data-promo'],
 'agent-reasoning-forgetting-externalized-state':['data-case','data-e','data-k'],
 'tsfm-sparse-event-ranking':['data-b21'],
 'zalando-sales-event-pricing-forecast-optimize':['data-zoutput','data-enable-select'],
 'orpr-or-guided-pretrain-reinforce-inventory':['data-b21'],
 'ra-dfl-risk-aware-decision-focused-inventory':['data-b21'],
 'flashtrie-gpu-beam':['data-b17'],
 'onetrans-v2-cascade-unification':['data-b21'],
}
LEGACY_SVG=['otto-gbdt-vs-dnn-ltr','multi-harness-rl','autolr-dashen','sid-ope-hierarchy','walmart-demand-transfer','harness-r1']
NOJS=LEGACY_SVG+['spotify-incremental-recommendation-causal','vn2-stockout-catboost','zalando-sales-event-pricing-forecast-optimize']

REFS=['reasoncast-agentic-demand-forecasting','retailbench-long-horizon-store-agents']

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__();self.tags=[];self.links=[];self.assets=[];self.ids=set();self.feed(text)
    def handle_starttag(self, tag, pairs):
        a=dict(pairs);self.tags.append((tag,a))
        if a.get('id'):self.ids.add(a['id'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag in ('img','script','iframe','link'):
            v=a.get('href') if tag=='link' else a.get('src')
            if v:self.assets.append(v)

def assert_paper_heading(page):
    # Embedded Markdown sections can contain their own h1; the hero identifies
    # the loaded paper. Require exactly one visible hero with the page title.
    heading = page.locator('main#paper > header.paper-hero > h1')
    assert heading.count() == 1, 'Expected exactly one paper hero heading'
    assert heading.is_visible(), 'Paper hero heading is hidden'
    text = heading.inner_text().strip()
    assert text, 'Paper hero heading is empty'
    assert page.title() == f'{text} | 研究ライブラリ', 'Paper hero heading does not match document title'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def preflight(site):
    pages=sorted((site/'papers').glob('*.html'))
    assert len(pages)==106, f'Expected all 106 pages, got {len(pages)}'
    assert_catalog(p.stem for p in pages)
    guide_pages=sorted((site/'guides').glob('*.html'))
    assert {p.name for p in guide_pages}=={'index.html','shelf-decisions.html'}
    docs={p:Document(p.read_text()) for p in [site/'index.html',*pages,*guide_pages]}
    assert {'wrapped-outcome','wrapped-time','wrapped-ci','wrapped-control','wrapped-shock',
            'wrapped-mismatch','wrapped-reset','wrapped-simulation'} <= docs[site/'papers'/f'{WRAPPED}.html'].ids
    checked=set();external=set()
    for path,doc in docs.items():
        for link in doc.links+doc.assets:
            u=urlsplit(urljoin(path.as_uri(),link))
            if u.scheme in ('http','https'):
                external.add(link);continue
            if u.scheme!='file':continue
            target=Path(unquote(u.path)).resolve()
            assert target.is_relative_to(site), (path,link,'outside build')
            assert target.is_file(),(path,link,'missing')
            if u.fragment and target.suffix=='.html':
                other=docs.get(target) or Document(target.read_text())
                assert unquote(u.fragment) in other.ids,(path,link,'fragment missing')
            checked.add(str(target.relative_to(site)))
    for slug,attrs in DISPLAY.items():
        doc=docs[site/'papers'/f'{slug}.html']
        for attr in attrs:assert any(attr in a for _,a in doc.tags),(slug,attr)
    for slug in EXPLORERS:
        doc=docs[site/'papers'/f'{slug}.html']
        assert any(a.get('data-interactive')=='explorer' for _,a in doc.tags),slug
        assert any('data-axes' in a for _,a in doc.tags),slug
    for slug in REFS:
        doc=docs[site/'papers'/f'{slug}.html']
        for a in ['data-reference-lab','data-json','data-export','data-import','data-error']:
            assert any(a in tag for _,tag in doc.tags),(slug,a)
    assert {'trace-agent','trace-alias','trace-normalize','trace-reset','trace-output'} <= docs[site/'papers'/f'{TRACE}.html'].ids
    shelf_ids={SHELF[0]:['controls','download','summary','selection','comparisons'],SHELF[1]:['case','S','f','t','lambda','beta','mode','rows','flows','download'],SHELF[2]:['experiment','nu','beta','y','t','candidate','candidate-view','download']}
    for slug,ids in shelf_ids.items():
        doc=Document((site/'downloads'/slug/'interactive.html').read_text())
        assert set(ids)<=doc.ids,(slug,set(ids)-doc.ids)
        assert all((site/'downloads'/slug/f).is_file() for f in ['interactive.js','model.js','results.json'])
    assert {'ep-task','ep-mask','ep-irrelevant','ep-setting','ep-policy','ep-timing','ep-next','ep-end','ep-reset','ep-output'} <= docs[site/'papers'/f'{EPISEM}.html'].ids
    required=[f'trace-{w}' for w in (360,390,768,1440)]+['nojs-'+TRACE]
    required += [f'episem-{w}' for w in (360,768,1440)]+['nojs-'+EPISEM]
    required += [f'wrapped-{w}' for w in (360,1440)]+['nojs-'+WRAPPED]
    required+=['compatibility','local-http-links','reference-independent-metrics-curves-save-reload']
    required += [f'load-{p.stem}-{w}' for w in (360,768,1440) for p in pages]
    required += [f'library-search-{w}' for w in (360,768,1440)]
    required += [f'guide-navigation-{w}' for w in (360,1440)]
    required += [f'shelf-survey-{w}' for w in (360,768,1440)]
    required += [f'detail-{slug}-{w}' for w in (360,1440) for slug in sorted(set(EXPLORERS+STATIC+list(DISPLAY)))]
    required += [f'shelf-{slug}-{w}' for w in (360,1440) for slug in SHELF]
    required += [f'nojs-{slug}' for slug in NOJS]+[f'svg-bounds-{slug}' for slug in LEGACY_SVG]
    sources=['episem_review.py','trace_review.py','catalog_expectations.py','wrapped_review.py','shelf_survey_browser.py','review_103_report.py','review_103_external.py','review_103.py','review_103_capture.py','review_103_evidence.py','reference_browser.py','macos_chrome_cdp.py','macos_cdp_review.py']
    for name in sources:ast.parse((ROOT/'tests'/name).read_text(),filename=name)
    # Known existing dependency only. No browser engine is imported or launched here.
    result={'status':'CONFIRMED preflight only','pages':106,'theme_guides':1,'guide_pages':2,'local_targets':len(checked),'local_paths':sorted(checked),
      'external_urls_listed_not_requested':len(external),'widths':[360,768,1440],'detailed_widths':[360,1440],'trace_widths':[360,390,768,1440],
      'required_cases':required,'semantic_groups':[[slug,w] for w in (360,1440) for slug in sorted(set(EXPLORERS+list(DISPLAY)+[WRAPPED]))]+[[TRACE,w] for w in (360,390,768,1440)]+[[EPISEM,w] for w in (360,768,1440)],
      'browser':'NOT TESTED','launch':'NOT TESTED on this host',
      'host_platform':platform.system(),'source_hashes':{n:digest(ROOT/'tests'/n) for n in sources+['main_103_catalog.json','main_104_catalog.json','main_105_catalog.json','main_105_review_cases.json']},
      'page_hashes':{p.relative_to(site).as_posix():digest(p) for p in docs},
      'planned_detailed_pages':sorted(set(SHELF+EXPLORERS+STATIC+list(DISPLAY)+REFS+[WRAPPED,TRACE,EPISEM])),
      'shelf_restore':'No import control exists. Download, reload, replay saved controls, re-download and compare. Never claim native import support.'}
    return result


def change(locator,value):
    locator.evaluate('(e,v)=>{e.value=String(v);e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}));}',str(value))


def settled(page):
    page.evaluate('()=>{for(const i of document.images)i.loading="eager"}')
    page.wait_for_function('document.fonts.status==="loaded" && [...document.images].every(i=>i.complete && i.naturalWidth>0)')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),page.url


def save_json(page,button,path):
    with page.expect_download() as download:button.click()
    download.value.save_as(path)
    return json.loads(path.read_text())


def assert_polyline(points, values, count, low, high):
    pairs=[tuple(map(float,p.split(','))) for p in points.split()]
    assert len(pairs)==len(values), 'Polyline point count differs from saved series'
    for i,((x,y),value) in enumerate(zip(pairs,values,strict=True)):
        assert math.isclose(x,48+440*i/max(1,count-1),abs_tol=1e-7)
        assert math.isclose(y,204-176*(value-low)/(high-low or 1),abs_tol=1e-7)
    return pairs


def forgetting_bound_text(e,k):
    return f'ε={e:.3f}, K={k} → TV ≤ 1−(1−ε)^K = {1-(1-e)**k:.3f} ≤ min(1,Kε) = {min(1,k*e):.3f}'


def assert_changed_output(page, control):
    """Return explicit coverage; an exercised input alone is never output evidence."""
    panel=control.locator('xpath=ancestor::*[@data-b18 or @data-b21][1]')
    if panel.count():
        frames=json.loads(panel.locator('[data-frames]').text_content())
        assert control.locator('option').count()==len(frames)
        expected=frames[int(control.input_value())]
        assert panel.locator('[data-output]').evaluate('(e,s)=>{const d=document.createElement("div");d.innerHTML=s;return e.innerHTML===d.innerHTML;}',expected)
        return 'CONFIRMED: selected saved frame including plot/table'
    panel=control.locator('xpath=ancestor::*[@data-interactive="explorer"][1]')
    if panel.count():
        d=json.loads(panel.locator('[data-results]').text_content());f=d['frames'][int(control.input_value())]
        rows=panel.locator('.bar-row').all();assert len(rows)==len(f['bars'])
        assert panel.locator('.explorer-note').inner_text()==f['note']
        for row,b in zip(rows,f['bars'],strict=True):
            shown=row.locator('strong').inner_text()
            assert shown=='推定不能' if b['value'] is None else math.isclose(float(shown.replace(',','')),b['value'],abs_tol=.000051)
        return 'CONFIRMED: selected explorer values and note'
    panel=control.locator('xpath=ancestor::*[@data-b17="slo"][1]')
    if panel.count():
        rows=json.loads(panel.locator('[data-values]').text_content());limit=float(control.input_value());ok=[r for r in rows if r[3]<=limit]
        text=panel.locator('[data-output]').inner_text()
        if not ok:assert '条件を満たすものはない' in text
        else:assert f'幅）は{ok[-1][0]}' in text and f'P@100={ok[-1][4]}' in text
        return 'CONFIRMED: SLO feasible maximum and P@100'
    if control.get_attribute('id')=='sparse-p':
        frames=json.loads(page.locator('#sparse-mass-data').text_content());expected=frames[int(control.input_value())-1]
        assert page.locator('[data-mass]').evaluate('(e,s)=>{const d=document.createElement("div");d.innerHTML=s;return e.innerHTML===d.innerHTML;}',expected)
        assert page.locator('#sparse-p-value').inner_text()==control.input_value()+'%'
        return 'CONFIRMED: probability frame and displayed probability'
    if control.get_attribute('id')=='zalando-slider':
        frames=json.loads(page.locator('[data-zframes]').text_content());expected=frames[int(control.input_value())]
        assert page.locator('[data-zoutput]').evaluate('(e,s)=>{const d=document.createElement("div");d.innerHTML=s;return e.innerHTML===d.innerHTML;}',expected)
        return 'CONFIRMED: selected pricing frame'
    batch=page.locator('[data-batch08]')
    if batch.count():
        d=json.loads(batch.text_content());kind=d['lab_kind']
        if kind=='sim08':
            row=d['traces'][page.locator('[data-cost]').input_value()][int(page.locator('[data-week]').input_value())]
            assert page.locator('[data-stock] .big').all_text_contents()==[f'{row[k]:.1f}' for k in ['before','inbound','sales','orders']]
            study=d['paper']['studies'][page.locator('[data-study]').input_value()]
            dots=page.locator('[data-transfer] circle').all();assert len(dots)==12
            for i in range(4):
                for j,(key,dx) in enumerate([('history',-15),('sim',10),('cal',30)]):
                    assert math.isclose(float(dots[3*i+j].get_attribute('cx')),105+i*135+dx,abs_tol=1e-7)
                    assert math.isclose(float(dots[3*i+j].get_attribute('cy')),255-study[key][i]*6,abs_tol=1e-7)
            return 'CONFIRMED: selected replay quantities and all published forecast dots'
        if kind=='harness08':
            n=int(page.locator('[data-n]').input_value());q=float(page.locator('[data-q]').input_value())
            item=next(x for x in d['power_grid'] if x['n']==n and x['q']==q)
            expected=['到達不可' if item[k] is None else f'{item[k]:.2f} pp' for k in ['mde50','mde80']]+[f'{item["ceiling"]*100:.1f}%']
            assert page.locator('[data-power] .big').all_text_contents()==expected
            rows=page.locator('[data-bill] tr').all();assert len(rows)==len(d['bill_params'])
            ratio=float(page.locator('[data-price]').input_value());actual=page.locator('[data-papersteps]').is_checked();compact=page.locator('[data-compact]').is_checked()
            for row,(name,(p,g,N)) in zip(rows,d['bill_params'].items(),strict=True):
                count=N if actual else int(page.locator('[data-steps]').input_value())
                total=sum(p+554+g*(k%60 if compact else k) for k in range(count))
                assert row.locator('th').inner_text()==name
                assert row.locator('td').all_text_contents()==[f'{p} / {g}',f'{total/1e6:.3f}',f'{total*(.03+.97*ratio)/1e6:.3f}']
            assert page.locator('[data-steps]').is_disabled()==actual
            return 'CONFIRMED: selected power grid and independently summed token bill'
        if kind=='traffic08':
            cases=d['cases'][page.locator('[data-actions]').input_value()]
            rows=page.locator('[data-toy] tr').all();assert len(rows)==len(cases)
            for row,(key,v) in zip(rows,cases.items(),strict=True):
                assert row.locator('td').all_text_contents()==[f'{v["mae"]:.3f}',f'{v["decision_loss"]:.3f}',f'{v["value_percent"]:.1f}%',', '.join(map(str,v['actions_used']))]
            assert ('正の価値あり' if cases['oracle']['value_percent']>0 else '価値ゼロ') in page.locator('[data-oracle]').inner_text()
            return 'CONFIRMED: all selected action-set costs and oracle condition'
        if kind=='hear08':
            sc=page.locator('[data-benchmark]').input_value()=='scbench';values=d['paper']['scbench' if sc else 'mooncake_100']
            rows=page.locator('[data-paper-rows] tr').all();assert len(rows)==len(values)
            assert page.locator('[data-paper-head] th').count()==len(values[0])
            for row,expected in zip(rows,values,strict=True):
                cells=row.locator('th,td').all_text_contents();assert len(cells)==len(expected)
                for shown,v in zip(cells,expected,strict=True):
                    assert float(shown)==v if isinstance(v,(float,int)) else shown==v
            assert ('SCBench' if sc else '100%負荷') in page.locator('[data-paper-note]').inner_text()
            return 'CONFIRMED: benchmark columns, complete rows and scope note'
    if page.locator('.exa-lab').count():
        av=float(page.locator('[data-a]').input_value());cv=float(page.locator('[data-c]').input_value())
        aa=1/(1+math.exp(-math.log(av/1.32)/.35));cc=1/(1+math.exp(-math.log(cv/.49)/.6))
        weights=[(1-aa)*(1-cc),aa*(1-cc),(1-aa)*cc,aa*cc];den=sum(v*v for v in weights)
        cells=page.locator('[data-weights] > div').all();assert len(cells)==4
        for cell,v in zip(cells,weights,strict=True):assert f'{v*100:.1f}% → {v*v/den*100:.1f}%' in cell.inner_text()
        assert math.isclose(float(page.locator('[data-point]').get_attribute('cx')),58+332*math.log(av)/math.log(12),abs_tol=1e-7)
        assert math.isclose(float(page.locator('[data-point]').get_attribute('cy')),242-222*math.log(cv/.01)/math.log(400),abs_tol=1e-7)
        S=int(page.locator('[data-stock]').input_value());inv=S;due=-1;latent=[];observed=[];promo=page.locator('[data-promo]').is_checked()
        for t in range(30):
            if t==due:inv=S;due=-1
            factor=(1.4 if 9<=t<12 else 2.4 if 12<=t<16 else .65 if 16<=t<20 else 1) if promo else 1
            demand=math.floor((7+3*math.sin(t*1.3))*factor+.5);sales=min(inv,demand);inv-=sales;latent.append(demand);observed.append(sales)
            if inv<8 and due<0:due=t+3
        paths=page.locator('[data-series] path').all();assert len(paths)==3
        for path,values in zip(paths[1:],[latent,observed],strict=True):
            assert path.get_attribute('d')==''.join(('M' if i==0 else 'L')+f'{42+i*19},{195-v*6}' for i,v in enumerate(values))
        assert page.locator('[data-lost]').inner_text()==f'潜在需要 {sum(latent)} 個のうち、観測されなかった需要は {sum(latent)-sum(observed)} 個。'
        return 'CONFIRMED: classification weights, coordinates, stock series and lost demand'
    if page.locator('[data-forget]').count():
        d=json.loads(page.locator('[data-forget]').text_content());c=d['cases'][page.locator('[data-case]').input_value()]
        assert page.locator('[data-trace] .step').count()==len(c['trace'])
        assert page.locator('[data-summary]').inner_text()==f'再導出 {c["rederivations"]}回 ／ 読出し {c["file_reads"]}回 ／ 人工労力 {c["effort_units"]}'
        e=float(page.locator('[data-e]').input_value());k=int(page.locator('[data-k]').input_value())
        assert page.locator('[data-bound]').inner_text()==forgetting_bound_text(e,k)
        return 'CONFIRMED: selected trace counts and independently calculated bound'
    return 'NOT TESTED: input exercised; semantic output assertion still required'


EXPLORER_DOM = r"""(panel, expectedWidths) => {
    const text = (root, selector) => [...root.querySelectorAll(selector)].map(e=>e.innerText);
    return {
        bars: [...panel.querySelectorAll('.bar-row')].map(row=>({
            strongs: text(row, 'strong'),
            widths: [...row.querySelectorAll('.bar-fill')].map(e=>e.style.width)})),
        tables: [...panel.querySelectorAll('table')].map(table=>({
            head: text(table, 'thead th'),
            rows: [...table.querySelectorAll('tbody tr')].map(row=>({
                heads: text(row, 'th'), cells: text(row, 'td')}))})),
        lines: [...panel.querySelectorAll('svg polyline')].map(e=>e.getAttribute('points')),
        text: panel.innerText,
        expectedWidths: expectedWidths.map(value=>{
            if (value === null) return null;
            const probe = document.createElement('div');
            probe.style.width = `${value}%`;
            return probe.style.width;
        })
    };
}"""


def explorer_dom(panel, widths=()):
    # Only read the fresh DOM. Expected percentages come from Python below;
    # JS serializes CSS numbers but neither calculates nor judges model values.
    assert all(v is None or (math.isfinite(v) and v >= 0) for v in widths)
    return panel.evaluate(EXPLORER_DOM, list(widths))


def assert_explorer_bars(dom, frame):
    rows=dom['bars'];assert len(rows)==len(frame['bars']), 'Bar count differs from saved frame'
    assert len(dom['tables'])==(2 if frame.get('lines') else 1), 'Unexpected table count'
    table_rows=dom['tables'][0]['rows'];assert len(table_rows)==len(rows)
    for row,item,tr in zip(rows,frame['bars'],table_rows,strict=True):
        assert len(row['strongs'])==1
        shown=row['strongs'][0]
        assert tr['heads']==[item['label']] and tr['cells']==[shown]
        if item['value'] is None:assert shown=='推定不能' and row['widths']==[]
        else:assert math.isclose(float(shown.replace(',','')),item['value'],abs_tol=.000051)


def assert_explorer_widths(dom, frame):
    assert len(dom['bars'])==len(dom['expectedWidths'])==len(frame['bars'])
    for row,item,expected in zip(dom['bars'],frame['bars'],dom['expectedWidths'],strict=True):
        if item['value'] is None:assert row['widths']==[] and expected is None
        else:
            assert expected.endswith('%')
            assert row['widths']==[expected]


def assert_explorer_lines(dom, frame, axes):
    lines=dom['lines'];series_list=frame.get('lines',[])
    assert len(lines)==len(series_list)
    if not series_list:return
    all_values=[v for s in series_list for v in s['values']];lo=min(0,*all_values);hi=max(1e-9,*all_values)
    n=max(len(s['values']) for s in series_list)
    assert len(dom['tables'])==2
    table=dom['tables'][1];assert len(table['rows'])==n
    assert len(table['head'])==len(series_list)+1
    heads=[h for row in table['rows'] for h in row['heads']]
    assert all(len(row['heads'])==1 for row in table['rows'])
    assert heads==[str(axes['start']+k) for k in range(n)]
    assert axes['caption'] in dom['text']
    # Cell counts are checked once per row, including all rows and extra cells.
    assert all(len(row['cells'])==len(series_list) for row in table['rows'])
    for j,(points,series) in enumerate(zip(lines,series_list,strict=True)):
        pts=assert_polyline(points,series['values'],n,lo,hi)
        for k,(x,y) in enumerate(pts):
            assert math.isclose(x,48+440*k/max(1,n-1),abs_tol=1e-7)
            assert math.isclose(y,204-176*(series['values'][k]-lo)/(hi-lo or 1),abs_tol=1e-7)
            shown=table['rows'][k]['cells'][j]
            assert math.isclose(float(shown.replace(',','')),series['values'][k],abs_tol=.000051)


def explorer_checks(page):
    for panel in page.locator('[data-interactive=explorer]').all():
        data=json.loads(panel.locator('[data-results]').text_content())
        axes=json.loads(panel.locator('[data-axes]').text_content())
        slider=panel.locator('input[type=range]')
        panel.locator('details').evaluate('(e)=>e.open=true')
        for i,frame in enumerate(data['frames']):
            change(slider,i)
            assert_explorer_bars(explorer_dom(panel),frame)
            scale=panel.get_by_role('button',name='棒の尺度：',exact=False)
            for local in (False,True):
                if (scale.get_attribute('aria-pressed')=='true')!=local:scale.click()
                values=[b['value'] for f in ([frame] if local else data['frames']) for b in f['bars'] if b['value'] is not None]
                maximum=max([1e-9,*values])
                widths=[None if b['value'] is None else 100*b['value']/maximum for b in frame['bars']]
                assert_explorer_widths(explorer_dom(panel,widths),frame)
            scale.click()  # Restore shared scale before subsequent state checks.
            assert scale.get_attribute('aria-pressed')=='false'
            assert_explorer_lines(explorer_dom(panel),frame,axes)
        panel.get_by_role('button',name='初期条件に戻す',exact=True).click()
        assert slider.input_value()==str(data['default'])
        assert panel.locator('.explorer-note').inner_text()==data['frames'][data['default']]['note']


def verify_saved_frames(page):
    """Compare actual post-switch markup including table/plot with saved frame."""
    for panel in page.locator('[data-b18], [data-b21]').all():
        frames=json.loads(panel.locator('[data-frames]').text_content())
        select=panel.locator('select');assert select.is_enabled()
        assert select.locator('option').count()==len(frames), 'Option/frame count differs'
        for i,frame in enumerate(frames):
            select.select_option(str(i))
            assert panel.locator('[data-output]').evaluate('(e,s)=>{const d=document.createElement("div");d.innerHTML=s;return e.innerHTML===d.innerHTML;}',frame)


def snapshot(page,out,name,region=None):
    from review_103_capture import capture
    settled(page)
    return capture(page,out/name,region)


def viewport_snapshot(page,out,name,evidence):
    """One initial viewport only; never tile the library or claim full-page coverage."""
    page.evaluate('scrollTo({top:0,left:0,behavior:"instant"})')
    filename=f'{name}-viewport-only.png'
    data=page.screenshot(path=str(out/filename),full_page=False,timeout=5000)
    evidence.report['screen_records'].append({
        'case':evidence.current,'page':page.url,'status':'CAPTURED initial viewport only',
        'file':filename,'viewport':page.viewport_size,'coverage':'initial viewport only; below-fold content not captured',
        'sha256':hashlib.sha256(data).hexdigest(),'manual_visual_review':'NOT TESTED'})
    evidence.persist()


def shelf_checks(page,base,out,slug,width):
    url=f'{base}/downloads/{slug}/interactive.html'
    assert page.goto(url).ok
    page.wait_for_function("document.querySelector('#summary').innerText.length>0")
    snapshot(page,out,f'{slug}-{width}-initial')
    if slug==SHELF[0]:
        def verify():
            result=page.evaluate('result');best=result['best']
            text=page.locator('#summary').inner_text()
            if best:
                assert f'{best["profit"]:.3f}' in text
                assert ':'.join(map(str,best['allocation'])) in text
                assert page.locator('#comparisons tr').first.locator('td').last.inner_text()==f'{best["profit"]:.3f}'
                capacity=page.evaluate('p.capacity')
                slots=page.locator('#shelf .shelf').last.locator('.slot')
                for i,cap in enumerate(best['allocation']):
                    assert_percent_width(slots.nth(i),100*cap/capacity)
                    assert_percent_width(slots.nth(i).locator('.used'),100*best['categories'][i]['used']/cap)
                    row=next(r for r in result['tables'][i] if r['capacity']==cap)['best']
                    table=page.locator('#selection table').nth(i)
                    for j,r in enumerate(row['rows']):
                        cells=table.locator('tbody tr').nth(j).locator('td').all_text_contents()
                        assert cells[:2]==[r['id'],str(r['faces'])]
                        assert cells[2:]==[f'{r[k]:.3f}' for k in ['direct','transfer','gross','replenishment','fixed']]
            else:assert '実行不能' in text
        verify()
        for key,val in dict(capacity=8,s=0,beta=0,r=0,c=0).items():change(page.locator('#control-'+key),val)
        verify();assert '16通り' in page.locator('#summary').inner_text()
        snapshot(page,out,f'{slug}-{width}-ties')
        for key,val in dict(capacity=2,e=1,brands=2).items():change(page.locator('#control-'+key),val)
        verify();snapshot(page,out,f'{slug}-{width}-infeasible')
        page.locator('#reset').click()
        page.locator('[data-cat="0"][data-cap="4"]').click()
        payload=save_json(page,page.locator('#download'),out/f'{slug}-{width}.json')
        page.reload();page.wait_for_function("document.querySelector('#summary').innerText.length>0")
        for k,v in payload['parameters'].items():change(page.locator('#control-'+k),v)
        for i,v in enumerate(payload['selected_detail_widths']):page.locator(f'[data-cat="{i}"][data-cap="{v}"]').click()
    elif slug==SHELF[1]:
        for case in ['T1','T2','T3','T4']:
            page.locator('#case').select_option(case)
            for mode in ['best','no_substitution','reevaluated','fixed']+(['t4'] if case=='T4' else []):
                change(page.locator('#mode'),mode)
                selected=page.evaluate("(()=>{const m=document.querySelector('#mode').value;return m==='best'?result.oracle.best:m==='fixed'?result.fixed_assortment.best:m==='t4'?ReplenishmentModel.evaluate(data,[0,1,0]):result[m]})()")
                if selected:
                    rows=page.locator('#rows tr');assert rows.count()==len(selected['rows'])
                    for i,r in enumerate(selected['rows']):
                        assert rows.nth(i).locator('td').all_text_contents()==[r['id'],str(r['k'])]+[f'{v:.3f}' for v in [r['direct'],r['transfer'],r['stock'],r['required'],max(0,-r['slack'])]]
                    active=[r for r in selected['rows'] if r['k']]
                    scale=max(1,*[v for r in selected['rows'] for v in [r['stock'],r['required']]])
                    stock_rows=page.locator('#bars > p').filter(has_text='棚在庫')
                    assert stock_rows.count()==len(active)
                    for j,r in enumerate(active):
                        stock_row=stock_rows.nth(j)
                        assert stock_row.inner_text().startswith(f'{r["id"]} 棚在庫')
                        stock_bar=stock_row.locator('.bar:not(.required)')
                        required_bar=stock_row.locator('.bar.required')
                        assert stock_bar.count()==required_bar.count()==1
                        assert_percent_width(stock_bar,60*r['stock']/scale)
                        assert_percent_width(required_bar,60*r['required']/scale)
                    assert f'{selected["profit"]:.3f}' in page.locator('#summary').inner_text()
                else:assert 'ありません' in page.locator('#summary').inner_text()
                snapshot(page,out,f'{slug}-{width}-{case}-{mode}',page.locator('#summary').locator('..'))
        page.locator('#case').select_option('T1');change(page.locator('#S'),0)
        assert '棚幅0' in page.locator('#shelf').inner_text()
        snapshot(page,out,f'{slug}-{width}-zero-width')
        page.locator('#reset').click();change(page.locator('#mode'),'reevaluated')
        payload=save_json(page,page.locator('#download'),out/f'{slug}-{width}.json')
        page.reload();page.wait_for_function("document.querySelector('#summary').innerText.length>0")
        d=payload['result']['input'];page.locator('#case').select_option(d['name'])
        # Snapshot chosen after reset: retain default lambda/t and replay actual edited S/f/beta.
        for k,v in {'S':d['S'],'f':d['items'][0]['f'],'beta':d['items'][0]['beta']}.items():change(page.locator('#'+k),v)
        change(page.locator('#mode'),payload['selected_mode'])
    else:
        for beta in [0,.5,1]:
            change(page.locator('#beta'),beta)
            for nu in [0,1,1.1,5,5.1,6]:
                change(page.locator('#nu'),nu)
                r=page.evaluate('saved.result');assert f'{r["best"]["profit"]:.6f}' in page.locator('#summary').inner_text()
                rows=page.locator('#rows tr');assert rows.count()==8
                for i,c in enumerate(r['candidates']):
                    assert rows.nth(i).locator('td').last.inner_text()==f'{c["profit"]:.6f}'
                    assert ('条件を満たす' in rows.nth(i).inner_text())==c['feasible']
                assert '白抜き点' in page.locator('#chart').inner_text()
                snapshot(page,out,f'{slug}-{width}-a-beta{beta}-nu{nu}',page.locator('#drawings'))
        page.locator('#candidate').select_option('3');assert '外枠超過' in page.locator('#candidate-view').inner_text()
        snapshot(page,out,f'{slug}-{width}-invalid-candidate',page.locator('#candidate-view'))
        page.locator('#experiment').select_option('b')
        for y,nu,t in [(4,1,1),(1,6,2),(4,.1,.1)]:
            for k,v in {'y':y,'nu':nu,'t':t}.items():change(page.locator('#'+k),v)
            assert page.locator('#rows tr').count()==36
            snapshot(page,out,f'{slug}-{width}-b-{y}-{nu}-{t}',page.locator('#drawings'))
        payload=save_json(page,page.locator('#download'),out/f'{slug}-{width}.json')
        page.reload();page.locator('#experiment').select_option(payload['type'])
        inp=payload['fixed']['input']
        for k,v in {'nu':inp['nu'],'y':inp['fixed_y'],'t':inp['thickness']}.items():change(page.locator('#'+k),v)
        page.locator('#candidate').select_option(str(payload['selected_candidate']))
    again=save_json(page,page.locator('#download'),out/f'{slug}-{width}-restored.json')
    assert again==payload,'Saved inputs replayed through controls must reproduce downloaded result'
    snapshot(page,out,f'{slug}-{width}-restored')


def external_check(url):
    try:
        with urlopen(Request(url,method='HEAD',headers={'User-Agent':'paper-lab-link-review/1.0'}),timeout=12) as r:
            return {'url':url,'status':r.status,'final_url':r.url,'result':'CONFIRMED HTTP reachability only'}
    except Exception as e:return {'url':url,'result':'PARTIAL / not confirmed','error':str(e)}


def _runtime(site,out,plan,evidence):
    runtime_started=time.monotonic()
    # The sole launch route is the previously successful protected macOS route.
    from macos_chrome_cdp import chrome_process,connect_checked_cdp,verify_seatbelt
    from importlib.metadata import version
    assert version("playwright")=="1.63.0", "Use the previously verified pinned Playwright version"
    from playwright.sync_api import sync_playwright
    from reference_browser import local_site
    import reference_browser
    report=evidence.report
    task=evidence.case
    def guard(browser):
        try:verify_seatbelt(browser)
        except Exception as e:raise ProtectionStop(str(e)) from e
    with chrome_process() as (endpoint,pid):
        report['browser']='STARTED'
        os.environ.update(LAB_CDP_URL=endpoint,LAB_CHROME_PID=str(pid),LAB_BROWSER='macos-cdp')
        # Reuse existing HTTP/input/upload/download/CDP compatibility checks, no fallback engine.
        import macos_cdp_review
        task('compatibility',lambda:macos_cdp_review.compatibility(out/'compatibility',on_failure=evidence.capture_failure,protection_check=guard),fatal=True)
        report['phase']='inspection'
        with local_site(site) as base,sync_playwright() as pw:
            browser=connect_checked_cdp(pw)
            try:
                report['engine']=browser.version
                source_urls=set()
                with ThreadPoolExecutor(max_workers=4) as pool:
                    local=list(pool.map(external_check,[base+'/'+p for p in plan['local_paths']]))
                report['local_http_links']=local
                def check_links():
                    assert all(x.get('status')==200 for x in local),'Built local links failed HTTP checks'
                task('local-http-links',check_links)
                for width in (360,768,1440):
                    page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1,reduced_motion='reduce',accept_downloads=True)
                    evidence.page=page
                    page.on('pageerror',lambda e,p=page:evidence.event('pageerror',e,p))
                    page.on('requestfailed',lambda r,p=page:evidence.event('requestfailed',r.url+' '+str(r.failure),p))
                    page.on('console',lambda msg,p=page:evidence.event('console-error',msg.text,p) if msg.type=='error' else None)
                    page.on('response',lambda r,p=page:evidence.event('http-error',f'{r.status} {r.url}',p) if r.status>=400 and r.url.startswith(base) else None)
                    def survey_rendering():
                        guard(browser)
                        from shelf_survey_browser import inspect_survey
                        inspect_survey(page,base,out,width,snapshot)
                    task(f'shelf-survey-{width}',survey_rendering)
                    def guide_navigation():
                        assert page.goto(base+'/index.html').ok;settled(page)
                        assert page.locator('[data-paper]').count()==106
                        page.get_by_role('navigation',name='読む入口').get_by_role('link',name='テーマガイド',exact=True).click();settled(page)
                        assert page.url.endswith('/guides/index.html')
                        snapshot(page,out,f'guide-index-{width}')
                        page.locator('[data-guide-link]').click();settled(page)
                        assert page.url.endswith('/guides/shelf-decisions.html')
                        assert '106件のLab ／ 1件のテーマガイド' in page.locator('main').inner_text()
                        snapshot(page,out,f'shelf-guide-{width}')
                        for slug in SHELF:
                            page.locator(f'.guide-body a[href="../papers/{slug}.html"]').first.click();settled(page)
                            assert page.url.endswith(f'/papers/{slug}.html')
                            page.get_by_role('link',name='棚割りのテーマガイドへ',exact=True).click();settled(page)
                            assert page.url.endswith('/guides/shelf-decisions.html')
                        page.get_by_role('navigation',name='読む入口').get_by_role('link',name='最新研究・Lab一覧',exact=True).click();settled(page)
                        assert page.locator('[data-paper]').count()==106
                    if width!=768:task(f'guide-navigation-{width}',guide_navigation)
                    def library_search():
                        assert page.goto(base+'/index.html').ok;settled(page)
                        assert page.locator('[data-paper]:visible').count()==106
                        if width in (360,1440):
                            guard(browser)
                            viewport_snapshot(page,out,f'library-initial-{width}',evidence)
                        page.get_by_role('searchbox').fill('2609.04518')
                        assert page.locator('[data-paper]:visible').count()==1
                        page.get_by_role('searchbox').fill('no-such-paper-xyz')
                        assert page.locator('[data-paper]:visible').count()==0 and page.locator('[data-empty]').is_visible()
                        page.get_by_role('button',name='条件を消去',exact=True).click()
                        assert page.locator('[data-paper]:visible').count()==106
                    task(f'library-search-{width}',library_search)
                    for path in sorted((site/'papers').glob('*.html')):
                        def visit(path=path):
                            assert page.goto(f'{base}/papers/{path.name}').ok
                            guard(browser);settled(page)
                            assert_paper_heading(page)
                            assert page.locator('[data-interactive][data-ready=true]').count()==page.locator('[data-interactive]').count()
                            if width in (360,1440) and path.stem=='proximal-residual-value-inventory-placement':
                                guard(browser)
                                viewport_snapshot(page,out,f'{path.stem}-initial-{width}',evidence)
                            for a in page.locator('.paper-actions a').all():
                                href=a.get_attribute('href')
                                if href.startswith('http'):source_urls.add(href)
                            for iframe in page.locator('iframe').all():
                                iframe.scroll_into_view_if_needed()
                                frame=iframe.element_handle().content_frame()
                                assert frame is not None
                                frame.wait_for_function("document.querySelector('#summary') && document.querySelector('#summary').innerText.length>0")
                                assert frame.evaluate('document.documentElement.scrollWidth<=innerWidth')
                            if width!=768:explorer_checks(page)
                        task(f'load-{path.stem}-{width}',visit)
                    if width==768:
                        page.close();continue
                    for slug in sorted(set(EXPLORERS+STATIC+list(DISPLAY))):
                        def detail(slug=slug):
                            page.goto(f'{base}/papers/{slug}.html');settled(page)
                            snapshot(page,out,f'{slug}-{width}-default')
                            if slug=='zalando-sales-event-pricing-forecast-optimize':
                                assert page.locator('#zalando-slider').count()==1 and page.locator('#zalando-slider').is_enabled()
                            if slug=='agent-reasoning-forgetting-externalized-state':
                                assert page.locator('[data-e]').input_value()=='0.02' and page.locator('[data-k]').input_value()=='30'
                                report['action_checks'].append({'slug':slug,'width':width,'state':'initial','status':assert_changed_output(page,page.locator('[data-e]'))})
                                for e,k in [(0.02,30),(0.035,17),(0.02,30)]:
                                    change(page.locator('[data-e]'),e);change(page.locator('[data-k]'),k)
                                    report['action_checks'].append({'slug':slug,'width':width,'e':e,'k':k,'status':assert_changed_output(page,page.locator('[data-e]'))})
                            verify_saved_frames(page)
                            # Exercise each existing selector and numeric slider through UI events.
                            controls=page.locator('select, input[type=range], input[type=checkbox]').all()
                            controls.sort(key=lambda c: c.get_attribute('type')!='checkbox')
                            for i,control in enumerate(controls):
                                if not control.is_visible():continue
                                assert control.is_enabled(), f'Expected enabled control {i} on {slug}'
                                tag=control.evaluate('(e)=>e.tagName')
                                if tag=='SELECT':
                                    options=control.locator('option').evaluate_all('(xs)=>xs.filter(x=>!x.disabled&&!x.hidden).map(x=>x.value)')
                                    for value in options:
                                        control.select_option(value)
                                        report['action_checks'].append({'slug':slug,'width':width,'control':i,'value':value,'status':assert_changed_output(page,control)})
                                elif control.get_attribute('type')=='checkbox':
                                    for checked in (True,False):
                                        control.set_checked(checked);assert control.is_checked()==checked
                                        report['action_checks'].append({'slug':slug,'width':width,'control':i,'value':checked,'status':assert_changed_output(page,control)})
                                else:
                                    for key in ('Home','End'):
                                        control.focus();control.press(key)
                                        report['action_checks'].append({'slug':slug,'width':width,'control':i,'value':control.input_value(),'status':assert_changed_output(page,control)})
                                region=control.locator('xpath=ancestor::*[self::figure or self::section][1]')
                                snapshot(page,out,f'{slug}-{width}-control-{i}',region if region.count() else None)
                            # The traffic/HEAR views use buttons rather than selects.
                            for attr in ('data-gate','data-reset','data-event-index'):
                                for button in page.locator(f'button[{attr}]').all():
                                    if button.is_enabled():
                                        button.click()
                                        if attr=='data-gate':
                                            assert button.get_attribute('aria-pressed')=='true'
                                            assert page.locator('[data-gate][aria-pressed=true]').count()==1
                                            assert page.locator('[data-gate-detail] h4').inner_text()==button.text_content()
                                        elif attr=='data-reset':
                                            assert page.locator('[data-messages] .message.on').count()==1
                                            assert page.locator('button[data-next]').is_enabled()
                                        else:
                                            assert page.locator('.request.selected').count()==1
                                            assert 'selected' in button.get_attribute('class').split()
                                            d=json.loads(page.locator('[data-batch08]').text_content())
                                            event=d['cases'][button.get_attribute('data-policy')]['trace'][int(button.get_attribute('data-event-index'))]
                                            text=page.locator('[data-event]').inner_text()
                                            assert event['id'] in text and f"TTFT {event['ttft']:g}" in text and f"開始 {event['start']:g}" in text
                                        report['action_checks'].append({'slug':slug,'width':width,'button':attr,'status':'CONFIRMED: selected gate/message/request output'})
                            next_button=page.locator('button[data-next]')
                            if next_button.count():
                                for _ in range(10):
                                    if not next_button.is_enabled():break
                                    before=page.locator('[data-messages] .message.on').count()
                                    next_button.click()
                                    assert page.locator('[data-messages] .message.on').count()==before+1
                                    assert page.locator('[data-force]').inner_text().strip()
                                assert next_button.is_disabled()
                            snapshot(page,out,f'{slug}-{width}-after-switches')
                        task(f'detail-{slug}-{width}',detail)
                    def wrapped_detail():
                        guard(browser)
                        assert page.goto(f'{base}/papers/{WRAPPED}.html').ok
                        settled(page)
                        assert_paper_heading(page)
                        inspect_wrapped(page, ROOT/'papers'/WRAPPED/'results.json')
                        report['action_checks'].append({'slug':WRAPPED,'width':width,'status':'CONFIRMED: all 6 reported and 27 synthetic states, geometry, keyboard and reset'})
                        snapshot(page,out,f'{WRAPPED}-{width}-checked')
                    task(f'wrapped-{width}',wrapped_detail)
                    for slug in SHELF:task(f'shelf-{slug}-{width}',lambda slug=slug:shelf_checks(page,base,out,slug,width))
                    page.close()
                # Reuse the existing guarded browser; no independent launch path.
                for trace_width in (360,390,768,1440):
                    trace_page=browser.new_page(viewport={'width':trace_width,'height':900},device_scale_factor=1)
                    evidence.page=trace_page
                    trace_page.on('pageerror',lambda error,p=trace_page:evidence.event('pageerror',error,p))
                    trace_page.on('requestfailed',lambda r,p=trace_page:evidence.event('requestfailed',r.url+' '+str(r.failure),p))
                    trace_page.on('console',lambda message,p=trace_page:evidence.event('console-error',message.text,p) if message.type=='error' else None)
                    trace_page.on('response',lambda r,p=trace_page:evidence.event('http-error',f'{r.status} {r.url}',p) if r.status>=400 and r.url.startswith(base) else None)
                    def trace_detail():
                        guard(browser)
                        assert trace_page.goto(f'{base}/papers/{TRACE}.html').ok
                        settled(trace_page)
                        assert_paper_heading(trace_page)
                        inspect_trace(trace_page, ROOT/'papers'/TRACE/'results.json')
                        report['action_checks'].append({'slug':TRACE,'width':trace_width,'status':'CONFIRMED: 12 states, operations, scores, hashes, bars, reset and keyboard'})
                        snapshot(trace_page,out,f'{TRACE}-{trace_width}-checked')
                    task(f'trace-{trace_width}',trace_detail)
                    trace_page.close()
                # Reuse the existing guarded browser; no independent launch path.
                for episem_width in (360,768,1440):
                    episem_page=browser.new_page(viewport={'width':episem_width,'height':900},device_scale_factor=1)
                    evidence.page=episem_page
                    episem_page.on('pageerror',lambda error,p=episem_page:evidence.event('pageerror',error,p))
                    episem_page.on('requestfailed',lambda r,p=episem_page:evidence.event('requestfailed',r.url+' '+str(r.failure),p))
                    episem_page.on('console',lambda message,p=episem_page:evidence.event('console-error',message.text,p) if message.type=='error' else None)
                    episem_page.on('response',lambda r,p=episem_page:evidence.event('http-error',f'{r.status} {r.url}',p) if r.status>=400 and r.url.startswith(base) else None)
                    def episem_detail():
                        guard(browser)
                        assert episem_page.goto(f'{base}/papers/{EPISEM}.html').ok
                        settled(episem_page)
                        assert_paper_heading(episem_page)
                        inspect_episem(episem_page, ROOT/'papers'/EPISEM/'results.json')
                        report['action_checks'].append({'slug':EPISEM,'width':episem_width,'status':'CONFIRMED: twins, persistent omissions, audit timing, task-weighted metrics, controls and keyboard reset'})
                        snapshot(episem_page,out,f'{EPISEM}-{episem_width}-checked')
                    task(f'episem-{episem_width}',episem_detail)
                    episem_page.close()
                nojs=browser.new_page(java_script_enabled=False,viewport={'width':360,'height':900})
                evidence.page=nojs
                nojs.on('requestfailed',lambda r:evidence.event('requestfailed',r.url+' '+str(r.failure),nojs))
                nojs.on('response',lambda r:evidence.event('http-error',f'{r.status} {r.url}',nojs) if r.status>=400 else None)
                try:
                    def wrapped_fallback():
                        assert nojs.goto(f'{base}/papers/{WRAPPED}.html',wait_until='load').ok
                        guard(browser)
                        assert_paper_heading(nojs)
                        assert_wrapped_initial(nojs, ROOT/'papers'/WRAPPED/'results.json')
                        assert nojs.locator('noscript:visible').count()==2
                        assert nojs.evaluate('document.documentElement.scrollWidth<=innerWidth')
                        nojs.screenshot(path=str(out/f'{WRAPPED}-360-nojs.png'),full_page=False)
                    task('nojs-'+WRAPPED,wrapped_fallback)
                    def trace_fallback():
                        assert nojs.goto(f'{base}/papers/{TRACE}.html',wait_until='load').ok
                        guard(browser)
                        assert_paper_heading(nojs)
                        assert_trace_initial(nojs, ROOT/'papers'/TRACE/'results.json')
                        assert nojs.locator('#trace-toy noscript').is_visible()
                        assert nojs.evaluate('document.documentElement.scrollWidth<=innerWidth')
                        nojs.screenshot(path=str(out/f'{TRACE}-360-nojs.png'),full_page=False)
                    task('nojs-'+TRACE,trace_fallback)
                    def episem_fallback():
                        assert nojs.goto(f'{base}/papers/{EPISEM}.html',wait_until='load').ok
                        guard(browser)
                        assert_paper_heading(nojs)
                        assert nojs.locator('#episem-toy noscript').is_visible()
                        assert 'JavaScript' in nojs.locator('#ep-output').inner_text()
                        assert nojs.evaluate('document.documentElement.scrollWidth<=innerWidth')
                        nojs.screenshot(path=str(out/f'{EPISEM}-360-nojs.png'),full_page=False)
                    task('nojs-'+EPISEM,episem_fallback)
                    for slug in NOJS:
                        def fallback(slug=slug):
                            assert nojs.goto(f'{base}/papers/{slug}.html',wait_until='load').ok
                            guard(browser)
                            # Locator assertions and direct evaluation work without page JS timers.
                            assert_paper_heading(nojs)
                            assert nojs.locator('figure.teaching:visible').count()>=2
                            assert nojs.evaluate('document.documentElement.scrollWidth<=innerWidth')
                            assert nojs.locator('[data-fallback]:visible').count()==nojs.locator('[data-interactive]').count()
                            if slug.startswith('zalando'):
                                assert nojs.locator('#zalando-slider').is_disabled()
                                assert nojs.locator('[data-enable-select] select').is_disabled()
                                assert nojs.locator('noscript:visible').count()==2
                                assert 'α = 0.0' in nojs.locator('[data-zoutput]').inner_text()
                                assert 'Demand Error' in nojs.locator('[data-enable-select] [data-output]').inner_text()
                            nojs.screenshot(path=str(out/f'{slug}-360-nojs.png'),full_page=False)
                        task(f'nojs-{slug}',fallback)
                finally:nojs.close()
                svg_page=browser.new_page();evidence.page=svg_page
                svg_page.on('pageerror',lambda e:evidence.event('pageerror',e,svg_page))
                svg_page.on('requestfailed',lambda r:evidence.event('requestfailed',r.url+' '+str(r.failure),svg_page))
                try:
                    for slug in LEGACY_SVG:
                        def svg_bounds(slug=slug):
                            paths=sorted((site/'figures'/slug).rglob('*.svg'));assert paths
                            for path in paths:
                                assert svg_page.goto(base+'/'+path.relative_to(site).as_posix()).ok
                                guard(browser)
                                svg_page.evaluate('document.fonts.ready')
                                clipped=svg_page.evaluate("""() => {
                                    const v=document.documentElement.viewBox.baseVal;
                                    return [...document.querySelectorAll('text')].filter(t=>{
                                        const b=t.getBBox();return b.x<0||b.y<0||b.x+b.width>v.width+1||b.y+b.height>v.height+1;
                                    }).map(t=>t.textContent);
                                }""")
                                assert not clipped,(path.name,clipped)
                        task(f'svg-bounds-{slug}',svg_bounds)
                finally:svg_page.close()
                guard(browser)
            finally:browser.close()
        # The preceding sync_playwright context is fully exited before inspect opens its own.
        reference_browser.SITE=site;reference_browser.OUT=out/'reference';reference_browser.OUT.mkdir()
        with local_site(site) as reference_base:
            task('reference-independent-metrics-curves-save-reload',lambda:reference_browser.inspect(reference_base,on_failure=evidence.capture_failure,protection_check=guard))
        report['phase']='cleanup'
    report['mandatory_execution_completed']=True
    evidence.persist()
    # Chrome and reference checks have fully completed and cleaned up before any external HEAD work.
    from review_103_external import bounded_check
    report['phase']='external-reachability'
    try:
        elapsed=time.monotonic()-runtime_started
        budget=min(45,max(0,18*60-60-elapsed))
        report['external_links'],report['external_budget']=bounded_check(source_urls,out/'external',budget)
        report['external_budget'].update(elapsed_before_external=elapsed,reserve_seconds=60)
        report['external_status']='CONFIRMED reachability only' if all(x['result'].startswith('CONFIRMED') for x in report['external_links']) else 'PARTIAL / unconfirmed URLs remain'
    except Exception as error:
        report['external_links']=[{'url':u,'result':'NOT CONFIRMED','reason':'external worker failure'} for u in sorted(source_urls)]
        report['external_status']='NOT CONFIRMED'
        report['external_error']=str(error)
    return report


def runtime(site,out,plan):
    evidence=RunEvidence(out,plan);completed=False;interruption=None
    keys=('LAB_CDP_URL','LAB_CHROME_PID','LAB_BROWSER')
    previous={key:os.environ.get(key) for key in keys}
    try:
        _runtime(site,out,plan,evidence);completed=True
    except BaseException as error:
        interruption={**evidence.report.get('interrupted_case',evidence.diagnostic(error)),'phase':evidence.report['phase'],
            'kind':'protection' if isinstance(error,ProtectionStop) else 'interruption'}
        if isinstance(error,ProtectionStop):
            evidence.report['screen_records'].append({'case':interruption.get('case'),'status':'NOT CAPTURED','reason':'Protection not confirmed; no further page interaction'})
        else:evidence.capture_failure(error=error)
    finally:
        for key,value in previous.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value
        result=evidence.finalize(completed,interruption)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    m=p.add_mutually_exclusive_group(required=True);m.add_argument('--preflight',action='store_true');m.add_argument('--run',action='store_true')
    p.add_argument('--site',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();site=a.site.resolve();out=a.out.resolve()
    assert site.is_dir() and not out.is_relative_to(site),'Output must be separate from built site'
    assert not out.exists(),'Use a new output directory; existing evidence is never overwritten'
    plan=preflight(site);out.mkdir(parents=True);(out/'preflight.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
    if a.preflight:print(json.dumps(plan,ensure_ascii=False,indent=2));return
    if platform.system()!='Darwin':
        evidence=RunEvidence(out,plan)
        evidence.finalize(False,{'kind':'environment','type':'UnsupportedHost','phase':'startup','message':'The approved runtime route requires macOS; no fallback launch'})
        raise SystemExit(2)
    result=runtime(site,out,plan)
    if result.get('automatic_status')!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
