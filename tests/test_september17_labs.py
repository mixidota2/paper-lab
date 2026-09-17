"""Boundary tests for the seven independent September 17 explanatory experiments."""
import importlib.util
import json
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ['genpage-netflix-homepage', 'unirec-chain-of-attribute', 'agentx-kuaishou',
         'static-constrained-gr', 'flashtrie-gpu-beam', 'gatesid-coldstart-ranking',
         'coral-meta-config-harness']

def module(i):
    spec = importlib.util.spec_from_file_location(SLUGS[i], ROOT/'papers'/SLUGS[i]/'run.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

@pytest.mark.parametrize('i', range(7))
def test_results_reproduce_and_provenance_is_versioned(i):
    p = ROOT/'papers'/SLUGS[i]
    assert json.loads(json.dumps(module(i).compute())) == json.loads((p/'results.json').read_text())
    y = yaml.safe_load((p/'lab.yaml').read_text())
    assert y['source_review']['pdf_sha256'] in (p/'mapping.md').read_text()
    assert len(y['source_review']['pdf_sha256']) == 64
    assert y['source_review']['version'] in y['urls']['pdf']
    assert y['verification']['performance'] == 'NOT TESTED'
    for name in ['README.md', 'method.md', 'mapping.md']:
        assert (p/name).stat().st_size > 500

def test_candidate_set_survives_hybrid_but_conditioning_changes():
    m = module(0)
    assert m.decode(3, False)['candidate_violations'] > 0
    for head in range(4):
        x = m.decode(head)
        assert x['candidate_violations'] == 0
        flattened = [i for r in x['page'] for i in r['items']]
        assert len(flattened) == len(set(flattened))
    assert m.decode(1)['page'] == m.decode(3)['page']
    assert m.decode(0)['page'] != m.decode(3)['page']
    assert m.decode(1)['forward_calls'] < m.decode(3)['forward_calls']

def test_coa_bayes_denominator_and_capacity_infeasibility():
    m = module(1); x = m.compute()
    assert m.entropy([1,1,1,1]) == 2
    assert m.entropy([4,0]) == 0
    assert x['bayes_corrected'] == pytest.approx([.2,.8])
    assert x['capacity']['feasible']
    assert sum(x['capacity']['before']) == sum(x['capacity']['after'])
    assert not x['infeasible_heavy_item']['feasible']
    metrics = x['experiments'][1]['metrics']
    assert metrics['商品A']['p(f|y=1,u)'] > metrics['商品B']['p(f|y=1,u)']

def test_agent_veto_review_and_replay_are_distinct():
    m = module(2)
    assert m.judge(.3,.1,.2,'clear',14)['verdict'] == 'KEEP'
    assert m.judge(.3,.1,.2,'severe',14)['verdict'] == 'DISCARD'
    assert m.judge(.3,.1,.2,'moderate',14)['verdict'] == 'EXTEND'
    assert m.judge(.3,-.1,.2,'clear',14)['verdict'] == 'EXTEND'
    assert not m.admit([.1],[.9],False)['accepted']
    assert not m.admit([.9],[.1],True)['accepted']

def test_csr_handles_shared_prefix_and_excludes_old_valid_id():
    m = module(3); c = m.build(m.FRESH)
    assert m.walk((0,),c)
    assert m.walk((0,0,1),c)
    assert not m.walk((0,0,0),c) # Valid catalog ID, excluded by freshness.
    assert not m.walk((1,0),c)
    assert not m.walk((0,0,1,1),c)
    assert not m.walk((0,),m.build([]))
    assert len(m.compute()['constrained']) == 1
    assert m.compute()['post_filter'] == []

def test_wider_beam_and_depth_only_filter():
    m = module(4)
    assert m.beam(1)[0]['path'] != (1,2)
    assert m.beam(2)[0]['path'] == (1,2)
    assert all(x['valid'] for x in m.beam(4))
    assert any(not x['valid'] for x in m.beam(4,False))
    assert m.beam(0) == []

def test_gate_endpoints_and_alignment_weight():
    m = module(5)
    assert m.gfsa(0)['shared_attention'] == m.gfsa(0)['item_attention']
    assert m.gfsa(1)['shared_attention'] == m.gfsa(1)['sid_attention']
    for w in [0,.25,.5,.75,1]:
        assert sum(m.gfsa(w)['shared_attention']) == pytest.approx(1)
    assert m.compute()['cases'][0]['weighted_alignment_loss'] == 0
    assert m.info_nce(.9,[.1]) < m.info_nce(.1,[.9])

def test_projection_is_feasible_identity_and_nearest():
    m = module(6)
    assert m.project([2,3],10) == [2,3]
    assert m.project([5,1],4) == pytest.approx([4,0])
    assert m.project([5,1],0) == pytest.approx([0,0])
    assert m.project([8,7,5],10) == pytest.approx([14/3,11/3,5/3])
    for p in [[0,0,0],[10,20,30],[-1,2,3]]:
        x=m.project(p,10)
        assert min(x)>=0 and sum(x)<=10+1e-9
    with pytest.raises(ValueError):m.project([1],-1)
    chosen=m.discrete([2,2,1],[1,3,6],10)
    assert sum([1,3,6][i] for i in chosen)<=10
