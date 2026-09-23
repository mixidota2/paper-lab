"""Local estimator and acceptance boundaries; no production-performance claims."""
import importlib.util,json,shutil,subprocess,sys
from pathlib import Path
import pytest,yaml
ROOT=Path(__file__).resolve().parents[1]
ALL_SLUGS=['netflix-counterfactual-observability','unique-baidu-unified-retrieval-ranking','flashvector-unity-serving-stack-agent','youtube-music-llm-rationales-discovery','muser-baidu-long-sequence-multi-interest','hgenpush-kuaishou-heterogeneous-push-gr','t0-tsfm-forecasting-with-context']
SLUGS=[s for s in ALL_SLUGS if (ROOT/'papers'/s).is_dir()]
def module(slug):
 spec=importlib.util.spec_from_file_location(slug,ROOT/'papers'/slug/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@pytest.mark.parametrize('slug',SLUGS)
def test_standalone_reproduction(slug,tmp_path):
 d=ROOT/'papers'/slug;shutil.copy2(d/'run.py',tmp_path/'run.py')
 subprocess.run([sys.executable,str(tmp_path/'run.py')],check=True)
 assert json.loads((tmp_path/'results.json').read_text())==json.loads((d/'results.json').read_text())
 y=yaml.safe_load((d/'lab.yaml').read_text());assert y['source_review']['pdf_sha256'] in (d/'mapping.md').read_text()
 assert y['verification']['performance']=='NOT TESTED'
def test_snips_expected_weights_and_missing_support():
 m=module(ALL_SLUGS[0]);log=[(0,0,1,.25),(0,0,0,.75)]
 assert m.snips(log,[0])==pytest.approx(.75)
 assert m.snips(log,[0],10)==pytest.approx(.75)
 with pytest.raises(ValueError):m.snips(log,[1])
 with pytest.raises(ValueError):m.snips([(0,0,1,0)],[0])
 r=m.simulate();assert r['absolute_error']<.006
 assert m.exact(m.FULL)-m.exact(m.LOO)==pytest.approx(.04)
def test_code_balance_has_distance_cost():
 m=module(ALL_SLUGS[1]);codes=[[1,0],[0,1],[-1,0],[0,-1]];p=[.7,.1,.1,.1]
 plain=m.assign([.8,.6],codes,p,0);balanced=m.assign([.8,.6],codes,p,1)
 assert plain['code']==0 and balanced['code']==1
 assert plain['raw_distances'][0]<plain['raw_distances'][1]
 assert m.assign([.8,.6],codes,[.25]*4,4)['code']==0
 with pytest.raises(ValueError):m.assign([1,0],codes,[0,.5,.25,.25],1)
def test_gate_does_not_accept_local_only_gain():
 m=module(ALL_SLUGS[2]);c=dict(correct=True,local_ratio=2,stack_ratio=.98,p99_ms=200)
 assert m.decide(c).startswith('reject')
 assert m.decide({**c,'stack_ratio':1.2,'p99_ms':251}).startswith('reject')
 assert m.decide({**c,'stack_ratio':1.06}).startswith('remeasure')
 assert m.decide({**c,'stack_ratio':1.2,'p99_ms':250})=='accept'
 assert m.decide({**c,'stack_ratio':float('nan')}).startswith('reject')

def test_discovery_holdback_preserves_candidates():
 m=module(ALL_SLUGS[3]);p=m.canonicalize(['known','new','invented'],{'known':'k','new':'n'},{'k'})
 assert [x['id'] for x in p]==['n']
 assert m.serve(None)['source']=='heuristic fallback'
 assert [x['id'] for x in m.serve(p)['items']]==[x['id'] for x in m.serve(p,False)['items']]
 assert m.serve(p,False)['items'][0]['rationale'] is None

def test_pooling_covers_remainders_and_loses_order():
 m=module(ALL_SLUGS[4]);xs=list(range(10001));out=m.compress(xs)
 assert len(out)==1001 and sum(out)==sum(xs)
 assert out[-800:]==xs[-800:]
 assert m.pool([1,0],2)==m.pool([0,1],2)
 assert m.orthogonal_penalty([[1,0],[0,1]])==0
 assert m.orthogonal_penalty([[1,0],[1,0]])==.5

def test_author_path_constrains_video_prefix():
 m=module(ALL_SLUGS[5]);r=m.retrieve((1,),(7,1),{(1,):['v1']},{(7,1):['v1','v2'],(7,2):['v3']})
 assert r['merged']==['v1','v2']
 assert m.token_probs([0,0],[[1,0]])!=m.token_probs([0,0],[[0,1]])
 assert sum(m.token_probs([1000,0],[]))==pytest.approx(1)

def test_covariate_role_blocks_future_path_and_quantiles_are_ordered():
 m=module(ALL_SLUGS[6]);assert m.propagate(True) and not m.propagate(False)
 q=m.ordered_quantiles(0,[-20,-2,0,10]);assert all(a<b for a,b in zip(q,q[1:]))
 assert m.skill_audit(36.7,43)['lift_pp']==6.3
 assert m.skill_audit(36.7,43)['implied_geomean_loss_relative_change']==pytest.approx(-.09952606635)
