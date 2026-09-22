"""Check the batch's address, inventory and evidence boundaries."""
import importlib.util,json,subprocess,sys,shutil
from pathlib import Path
import pytest,yaml
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['varg-tmall-value-generative-retrieval','accuracy-not-service-intermittent-demand','aura-disney-agentic-rec-diagnosis']
def module(slug):
 spec=importlib.util.spec_from_file_location(slug,ROOT/'papers'/slug/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@pytest.mark.parametrize('slug',SLUGS)
def test_standalone_results_and_source_identity(slug,tmp_path):
 d=ROOT/'papers'/slug
 for p in d.iterdir():
  if p.suffix in {'.py','.csv'}:shutil.copy2(p,tmp_path/p.name)
 subprocess.run([sys.executable,str(tmp_path/'run.py')],check=True)
 assert json.loads((tmp_path/'results.json').read_text())==json.loads((d/'results.json').read_text())
 y=yaml.safe_load((d/'lab.yaml').read_text());assert y['source_review']['pdf_sha256'] in (d/'mapping.md').read_text()
 assert y['verification']['performance']=='NOT TESTED'
def test_varg_gate_and_address_boundaries():
 m=module(SLUGS[0]);old=m.assign({'a':.2,'b':.1});new=m.assign({'a':.2,'b':.1,'c':.9,'d':0},old)
 assert new['a']==old['a'] and new['b']==old['b']
 assert new['d']==1 and new['c']==0
 assert m.reward('malformed','buy',100)==-2
 assert m.reward('unoccupied','buy',100)==-1
 assert m.reward('occupied','buy',float('nan'))==3
 assert m.reward('occupied','click',0,1)==1
 assert sum(m.ordinal(2,3).values())==pytest.approx(1)
def test_stock_target_is_not_service_monotonicity():
 m=module(SLUGS[1]);orders=[[[3],[1],[1]]]
 assert m.replay(orders,[2])[0]==pytest.approx(2/3)
 assert m.replay(orders,[3])[0]==pytest.approx(1/3)
 for x in [[0,0],[0,4],[0,2,6]]:
  z,c,s=m.normalize(x,True);assert [v*s+c for v in z]==pytest.approx(x)
def test_aura_unknown_evidence_is_rejected():
 m=module(SLUGS[2]);f={'sessions':['real','invented'],'path':'real.py'}
 assert m.validate(f,{'real'},{'real.py'})==['unknown_session']
