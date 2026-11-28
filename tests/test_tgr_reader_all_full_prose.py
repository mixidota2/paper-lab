from pathlib import Path
import ast
import json
import runpy
from xml.etree import ElementTree as E

import pytest

from prose_preservation import before_contextual_all_full_prose, before_tgr_reader_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
P='papers/tgr/'
H='papers/_toy_common.py'


def pair(path):
    value=(ROOT/path).read_bytes()
    return before_tgr_reader_all_full_prose(ROOT,path,value),value


def test_tgr_explanation_rewrite_is_exact_and_does_not_move_figure_geometry():
    rows=json.loads((ROOT/'tests/tgr_reader_all_full_prose_hashes.json').read_text())['files']
    assert set(rows)=={H,*[P+n for n in ('results.json','run.py','figures/cascade.svg','figures/channel.svg','figures/ranking.svg')]}
    for name in rows:
        a,b=pair(name)
        assert a!=b
        with pytest.raises(AssertionError):
            before_tgr_reader_all_full_prose(ROOT,name,b+b'\n')
        if name.endswith('.svg'):
            sections=lambda raw:[(e.tag,e.attrib,len(e)) for e in E.fromstring(raw).iter()]
            assert sections(a)==sections(b)
    def no_doc(x):
        tree=ast.parse(x)
        assert isinstance(tree.body.pop(0).value,ast.Constant)
        return ast.dump(tree)
    assert no_doc(pair(P+'run.py')[0])==no_doc(pair(P+'run.py')[1])


def test_tgr_numeric_replay_and_non_target_shared_outputs(tmp_path):
    prior=tmp_path/'previous.py'
    prior.write_bytes(pair(H)[0])
    reviewed=tmp_path/'reviewed_tgr.py'
    reviewed.write_bytes(before_contextual_all_full_prose(ROOT,H,(ROOT/H).read_bytes()))
    old,new=map(runpy.run_path,(str(prior),str(reviewed)))
    assert old['IDS']==new['IDS'] and len(old['IDS'])==11
    for slug in old['IDS']:
        a,b=old['compute'](slug),new['compute'](slug)
        if slug=='tgr':
            assert (a,b)==tuple(map(json.loads,pair(P+'results.json')))
            assert a.pop('note')!=b.pop('note')
            assert a['experiments'][0].pop('name')!=b['experiments'][0].pop('name')
            for x,y in zip(a['explorer']['frames'],b['explorer']['frames'],strict=True):
                assert x.pop('note')!=y.pop('note')
            assert len(b['explorer']['frames'])==8
        assert a==b,slug
