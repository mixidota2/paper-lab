"""Independent arithmetic and trace-boundary tests for the teaching ledger."""
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import pytest

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'papers'/'trajectory-deletion-prefix-cost'
spec=importlib.util.spec_from_file_location('deletion_model',P/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

@pytest.mark.parametrize('a,b,want', [([],[],0),([],[1],0),([1],[],0),([1],[1],1),([1,2],[1,2,3],2),([1,2],[9,2],0),([1,2,3],[1,3],1),([1,1],[1,1],2),([1,2,1],[1,1,2],1),([2,1,1],[1,2,1],0)])
def test_lcp(a,b,want):
 assert m.lcp(a,b)==want

@pytest.mark.parametrize('q',[0,.1,1])
def test_exact_example(q):
 r=m.ledger([['a','b','c'],['a','c','d'],['a','c','d','e']],[1,2,0],q)
 assert [x['c'] for x in r['rows']]==[0,1,3]
 assert [x['rebilled'] for x in r['rows']]==[0,1,0]
 assert r['total']==pytest.approx(3+5+2+q+10+1+3*q)
 assert m.ledger([],[],q)['total']==0

@pytest.mark.parametrize('a',list(itertools.product((0,.5,.9,1),range(4),(2,4,6),(0,2,4))))
def test_all_conditions_independently(a):
 s=m.scenario(*a)
 for side in ('baseline','changed'):
  prev=[];total=0
  for r in s[side]['rows']:
   # Independent longest-prefix definition: max valid prefix length.
   current=r['prompt']
   assert len(current)==len(set(current)), 'Every generated teaching prompt uses unique IDs'
   c=max(k for k in range(min(len(prev),len(current))+1) if prev[:k]==current[:k])
   assert r['c']==c
   assert r['n']==len(current)==r['c']+r['new']+r['rebilled']
   total+=len(current)-c+(1-a[0])*c+5*r['output']
   prev=current
  assert s[side]['total']==pytest.approx(total)
 if a[1]==3: assert s['baseline']==s['changed']
 elif a[3]==0: assert s['changed']['tokens']<s['baseline']['tokens']
 if a[1]!=3 and a[3]: assert len(s['changed']['rows'])==7


def test_ranking_changes_without_discount():
 with_cache=m.scenario();flat=m.scenario(0,1,4,0)
 assert with_cache['changed']['total']>with_cache['baseline']['total']
 assert flat['changed']['total']<flat['baseline']['total']


def test_retrieval_cost_and_delay():
 assert m.scenario(.9,1,4,4)['changed']['total']>m.scenario()['changed']['total']
 assert m.scenario(.9,2,2,0)['rewrite_call']==4
 for r in m.scenario()['changed']['rows'][:3]: assert r['rebilled']==0


def test_results_and_regeneration():
 before={n:(P/n).read_bytes() for n in ['results.json','lab.yaml','experiment.md']}
 assert json.loads(before['results.json'])==m.results()
 subprocess.run(['uv','run','--locked','python',str(P/'run.py')],cwd=ROOT,check=True)
 assert before=={n:(P/n).read_bytes() for n in before}


def test_invalid():
 with pytest.raises(ValueError): m.ledger([[1]],[])
 with pytest.raises(ValueError): m.ledger([],[],2)
 with pytest.raises(ValueError): m.scenario(retrieval=-1)


def test_actual_javascript_render_and_reset(tmp_path):
    # Actual JS in a tiny document mock; no Chromium/CSSOM/runtime claim.
    script=r'''
const fs=require('fs'),vm=require('vm');
const data=JSON.parse(fs.readFileSync(process.argv[1]+'/results.json','utf8'));
const ids=['discount','position','timing','retrieval'];
const elements={};
for(const id of ids)elements['deletion-'+id]={value:({discount:.9,position:1,timing:4,retrieval:0})[id],addEventListener(k,f){this[k]=f;}};
elements['deletion-data']={textContent:JSON.stringify(data)};
elements['deletion-output']={innerHTML:''};
elements['deletion-reset']={addEventListener(k,f){this[k]=f;}};
vm.runInNewContext(fs.readFileSync(process.argv[1]+'/interactive.js','utf8'),{document:{getElementById:id=>elements[id]}});
const initial=elements['deletion-output'].innerHTML;
const frames=[];
for(const c of data.synthetic){for(const id of ids)elements['deletion-'+id].value=String(c.args[id]);elements['deletion-discount'].change();frames.push(elements['deletion-output'].innerHTML);}
elements['deletion-reset'].click();
if(elements['deletion-output'].innerHTML!==initial)throw Error('Reset failed');
console.log(JSON.stringify(frames));
'''
    frames=json.loads(subprocess.check_output(['node','-e',script,str(P)],text=True))
    from html.parser import HTMLParser
    class Tokens(HTMLParser):
        def __init__(self):super().__init__();self.tokens=[];self.active=False
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if tag=='span' and a.get('class','').startswith('token '):self.tokens.append([a['class'],'']);self.active=True
        def handle_data(self,s):
            if self.active:self.tokens[-1][1]+=s
        def handle_endtag(self,tag):
            if tag=='span':self.active=False
    assert len(frames)==144
    assert all('class="deletion-ledger tablewrap"' in html for html in frames)
    for c,html in zip(m.results()['synthetic'],frames):
        assert f"<strong data-changed>{c['changed']['total']:.2f}</strong>" in html
        parsed=Tokens();parsed.feed(html)
        expected=[];previous=[]
        for r in c['changed']['rows']:
            for j,t in enumerate(r['prompt']):
                cl='cached' if j<r['c'] else 'rebilled' if t in previous[r['c']:] else 'new'
                expected.append(['token '+cl,('↓' if j==r['first_changed'] else '')+t])
            previous=r['prompt']
        assert parsed.tokens==expected


def test_plan_keeps_all_main_cases_and_requires_new_semantics(tmp_path):
 from paper_lab.build import build
 import review_103 as review
 site=tmp_path/'site';build(root=ROOT,site_dir=site)
 plan=review.preflight(site)
 old=json.loads((ROOT/'tests/main_104_review_cases.json').read_text())
 trace='trace-verifier-brittleness';slug=P.name
 main_cases=set(old['required_cases'])|{f'trace-{w}' for w in (360,390,768,1440)}|{'nojs-'+trace}|{f'load-{trace}-{w}' for w in (360,768,1440)}
 assert len(main_cases)==399
 added={f'deletion-{w}' for w in (360,768,1440)}|{'nojs-'+slug}|{f'load-{slug}-{w}' for w in (360,768,1440)}
 episem='episem-missing-evidence-recovery'
 episem_cases={f'episem-{w}' for w in (360,768,1440)}|{'nojs-'+episem}|{f'load-{episem}-{w}' for w in (360,768,1440)}
 assert len(added)==len(episem_cases)==7
 arc='featurearc-inherited-defects-chain-gates'
 arc_cases={f'featurearc-{w}' for w in (360,768,1440)}|{'nojs-'+arc}|{f'load-{arc}-{w}' for w in (360,768,1440)}
 assert len(arc_cases)==7
 assert set(plan['required_cases'])==main_cases|added|episem_cases|arc_cases
 assert len(plan['required_cases'])==420
 assert all([slug,w] in plan['semantic_groups'] for w in (360,768,1440))
 assert 'deletion_review.py' in plan['source_hashes']


@pytest.mark.parametrize('a',list(itertools.product((0,.5,.9,1),range(3),(2,4),(2,4))))
def test_recovery_preserves_chronological_append_only_prefix(a):
 s=m.scenario(*a);rows=s['changed']['rows'];recovery_index=s['rewrite_call']
 recovery=rows[recovery_index]
 # Additional call only appends R; following ordinary calls append new turns
 # after R and reuse the entire prior prompt, with no hidden reordering.
 assert recovery['c']==len(rows[recovery_index-1]['prompt'])
 assert recovery['prompt'][-a[3]:]==[f'R{j}' for j in range(a[3])]
 for previous,current in zip(rows[recovery_index:],rows[recovery_index+1:]):
  assert current['prompt'][:len(previous['prompt'])]==previous['prompt']
  assert current['c']==len(previous['prompt'])
  assert current['rebilled']==0


def test_retrieval_two_has_no_hidden_reordering_surcharge():
 s=m.scenario(.9,1,4,2)
 assert s['changed']['total']==pytest.approx(95.9)
 assert [r['c'] for r in s['changed']['rows']]==[0,2,6,7,12,14,18]
 assert m.scenario()['baseline']['total']==pytest.approx(87)
 assert m.scenario()['changed']['total']==pytest.approx(87.3)
 assert m.scenario(0,1,4,0)['baseline']['total']==132
 assert m.scenario(0,1,4,0)['changed']['total']==126


@pytest.mark.parametrize('violation',[None,'old-fixed-columns','numeric-text','row-height','missing-cell','split-decimal','wrap-enabled','split-header'])
def test_ledger_geometry_detects_cross_cell_content(violation):
 from deletion_review import assert_ledger_geometry
 # Six disjoint cells. The old 640px fixed layout gave the token cell
 # roughly107px while its content required200px: viewport bounds still pass.
 row={'geometry':[{'box':[i*107,0,(i+1)*107,80],
                    'content':[[i*107+10,10,(i+1)*107-10,30]],
                    'textRects':[[i*107+10,10,(i+1)*107-10,30]],'whiteSpace':'nowrap'} for i in range(6)]}
 import copy
 row['headers']=copy.deepcopy(row['geometry'])
 if violation=='old-fixed-columns':row['geometry'][1]['content']=[[117,10,317,30]]
 if violation=='numeric-text':row['geometry'][2]['content']=[[180,10,260,30]]
 if violation=='row-height':row['geometry'][1]['content']=[[117,10,200,100]]
 if violation=='missing-cell':row['geometry'].pop()
 if violation=='split-decimal':
  # Both fragments remain inside the cost cell, so containment alone passes.
  row['geometry'][5]['textRects']=[[545,10,560,30],[545,35,560,55]]
  row['geometry'][5]['content']=row['geometry'][5]['textRects']
 if violation=='wrap-enabled':row['geometry'][2]['whiteSpace']='normal'
 if violation=='split-header':row['headers'][2]['textRects']=[[224,10,240,30],[224,35,240,55]]
 if violation is None:assert_ledger_geometry([row])
 else:
  with pytest.raises(AssertionError):assert_ledger_geometry([row])


def test_ledger_owns_scrollable_content_sized_layout():
 import re
 css=(P/'experiment.md').read_text().split('</style>',1)[0]
 rules=dict(re.findall(r'([^{}]+)\{([^{}]+)\}',css.split('<style>',1)[1]))
 table=rules['.deletion-ledger table']
 assert 'table-layout:auto' in table and 'min-width:800px' in table
 assert 'overflow-x:auto' in rules['.deletion-ledger']

 assert 'width:320px' in rules['.deletion-ledger th:nth-child(2),.deletion-ledger td:nth-child(2)']
 assert 'white-space:nowrap' in rules['.deletion-ledger thead th,.deletion-ledger tbody th,.deletion-ledger td:not(:nth-child(2))']
