"""Preserve the study identity, arithmetic, and source-byte review."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

import pytest
import yaml

from prose_preservation import before_scaffold_gaia_full_prose

ROOT = Path(__file__).resolve().parents[1]
REL = 'papers/scaffold-effects-gaia/'


def old(n):
    p = REL + n
    return before_scaffold_gaia_full_prose(ROOT, p, (ROOT / p).read_bytes())


def test_rewrite_does_not_change_study_identity_or_numerical_results():
    now = yaml.safe_load((ROOT / REL / 'lab.yaml').read_bytes())
    previous = yaml.safe_load(old('lab.yaml'))
    for k in ('id','arxiv_id','title','authors','urls','status','verification'):
        assert now[k] == previous[k]
    overview = now['sections']['overview']
    assert len(overview.split('\n\n')) == 3
    assert all(v in overview for v in ('84%', '56%', '最大28ポイント','14ポイント','5つのモデル','3回の試行'))
    assert all(v not in overview for v in ('Lab', '作例', '<figure', '<table'))
    a,b = (json.loads(x) for x in ((ROOT / REL / 'results.json').read_bytes(), old('results.json')))
    for v in (a,b):
        del v['note'],v['experiments'][0]['name'],v['explorer']['label']
        for f in v['explorer']['frames']:
            del f['note']
    assert a == b


def test_exact_source_and_readable_figures():
    expected = {'README.md','lab.yaml','method.md','results.json','run.py','figures/control-flow.svg','figures/evaluation-unit.svg','figures/recovery.svg'}
    receipt = json.loads((ROOT / 'tests/scaffold_gaia_full_prose_hashes.json').read_text())['files']
    assert set(receipt) == {REL + n for n in expected}
    for p in expected:
        raw=(ROOT / REL / p).read_bytes()
        assert raw!=old(p)
        with pytest.raises(AssertionError):
            before_scaffold_gaia_full_prose(ROOT,REL+p,raw+b'\n')
        if p.endswith('.svg'):
            svg=ET.fromstring(raw)
            assert svg.attrib['aria-labelledby']=='title' and svg.attrib['role']=='img' and svg.attrib['viewBox']
