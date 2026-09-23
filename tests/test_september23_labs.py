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
