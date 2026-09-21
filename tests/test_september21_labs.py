"""Semantic boundary tests: oracle, distribution shift, masks and SID ambiguity."""
import importlib.util,json
from pathlib import Path
import pytest,yaml
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['lige-gr-meta-listwise','sona-yandex-music','uvr-wolt-trial-reorder','pushdualgen-kuaishou','snaplgr-snapchat','sidscope-diagnostics']
def module(i):
 spec=importlib.util.spec_from_file_location(SLUGS[i],ROOT/'papers'/SLUGS[i]/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
@pytest.mark.parametrize('i',range(6))
def test_results_reproduce_and_claim_scope(i):
 p=ROOT/'papers'/SLUGS[i]
 assert json.loads(json.dumps(module(i).compute()))==json.loads((p/'results.json').read_text())
 y=yaml.safe_load((p/'lab.yaml').read_text())
 assert y['source_review']['html_sha256'] in (p/'mapping.md').read_text()
 assert y['source_review']['version'] in y['urls']['pdf']
 assert y['verification']['production_applicability']=='NOT TESTED'
def test_palette_wide_beam_matches_exact_oracle_and_fallback():
 m=module(0);r=m.compute()
 assert m.decode(1000)['shared_survival_value']==round(r['oracle']['value'],6)
 assert m.decode(budget=0)['path']==m.decode(contextual=False,survival=False)['path']
 for run in r['runs'].values():assert m.feasible(tuple(run['path']))
 assert r['runs']['trimmed_top3']['shared_survival_value']<=r['oracle']['value']
def test_distillation_unseen_feature_identifiability():
 m=module(1)
 assert m.train([m.data(1,40,False)])[2]==0
 assert m.train([m.data(1,40,True)])[2]<-1
 # Per-source mean is invariant to duplicating its observations.
 s=m.data(1,10,True)
 assert m.train([s],steps=1)==pytest.approx(m.train([s*2],steps=1))
def test_uvr_smoothing_and_eligibility_boundaries():
 m=module(2)
 assert m.smooth_target(0,3,0)==[1,0,0]
 assert sum(m.smooth_target(1,3))==pytest.approx(1)
 assert m.eligible_scores([100,1,2],[1,2])=={1:1,2:2}
 assert m.eligible_scores([100,1,2],[])=={}
def test_push_copy_is_optional_but_fusion_changes_candidates():
 m=module(3)
 for h in ('music','food'):
  assert m.decode(h)['sid']==m.decode(h,False)['sid']
  assert m.decode(h)['steps']>m.decode(h,False)['steps']
 assert m.rank(0)!=m.rank(1)
def test_snap_materialization_is_not_sid_accuracy():
 m=module(4);r=m.compute()['experiments'][0]['metrics']
 assert r['first_item']['SID_hit']==r['value_weighted']['SID_hit']
 assert r['value_weighted']['opposite_target_hit']==0
 assert r['first_item']['video_hit']<r['value_weighted']['video_hit']
def test_sid_collision_denominators_and_invalid_inputs():
 m=module(5);r=m.compute();d=r['experiments'][0]['metrics']['old']
 assert d['collision_item_rate']==pytest.approx(2/6)
 assert d['duplicate_SID_rate']==pytest.approx(1/6)
 assert r['trace_before']['target_path_survives'] and not r['trace_before']['unique_item_hit']
 assert r['trace_after']['unique_item_hit']
 for bad in ({},{'a':[0],'b':[0,1]},{'a':[-1]},{'a':[True]}):
  with pytest.raises(ValueError):m.diagnose(bad)
 official=r['official_quickstart_mapping']
 assert official['unique_leaves']==11
 assert official['collision_item_rate']==pytest.approx(2/12)
 assert [x['active_prefixes'] for x in official['profiles']]==[3,6,11]
