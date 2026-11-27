"""Keep the paper, simulation evidence and toy values separate and auditable."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

import pytest
import yaml

from prose_preservation import before_wholefoods_all_full_prose

ROOT = Path(__file__).resolve().parents[1]
REL = 'papers/whole-foods-shelf/'


def old(name):
    path = REL + name
    return before_wholefoods_all_full_prose(ROOT, path, (ROOT / path).read_bytes())


def test_study_and_overview_keep_the_original_scope():
    now = yaml.safe_load((ROOT / REL / 'lab.yaml').read_bytes())
    previous = yaml.safe_load(old('lab.yaml'))
    for key in ('id', 'doi', 'title', 'authors', 'urls', 'status', 'verification'):
        assert now[key] == previous[key]
    assert now['source_review']['url'] == previous['source_review']['url']
    overview = now['sections']['overview']
    markers = ['Liら', '商圏', '週販売数量', '既存手法', 'シミュレーション', '改装で7.5%', '新店設計で6.7%', '実際に改装や出店をした後の売上を測った結果ではなく']
    assert all(m in overview for m in markers)
    assert all(m not in overview for m in ('Lab', '教材', '操作図', '268.7006'))
    for before, after in zip(previous['teaching_figures'], now['teaching_figures'], strict=True):
        assert (before['source'], before['locator']) == (after['source'], after['locator'])
        assert [s['formula'] for s in before.get('steps', ())] == [s['formula'] for s in after.get('steps', ())]


def test_every_numeric_result_and_reference_formula_survives():
    before, after = (json.loads(x) for x in (old('results.json'), (ROOT / REL / 'results.json').read_bytes()))
    def numeric(x):
        if isinstance(x, dict):
            return [n for v in x.values() for n in numeric(v)]
        if isinstance(x, list):
            return [n for v in x for n in numeric(v)]
        return [x] if isinstance(x, (float, int)) else []
    assert len(numeric(before)) > 1700
    assert numeric(before) == numeric(after)
    assert before['verification'] == after['verification']
    frames = after['explorer']['frames']
    assert len(frames) == 21
    for frame in frames:
        assert len(frame['lines'][0]['values']) == 81
        vals = frame['lines'][0]['values']
        equal, best = (b['value'] for b in frame['bars'])
        assert equal == vals[40] and best == max(vals)
        assert '教材' in after['explorer']['metric']
        assert '購買後の長期効果を表さない' in frame['note']


def test_exact_full_prose_and_accessible_figures():
    expected = {'mapping.md','lab.yaml','method.md','results.json','run.py','figures/bias.svg','figures/pipeline.svg','figures/scenarios.svg'}
    receipt = json.loads((ROOT / 'tests/wholefoods_all_full_prose_hashes.json').read_text())['files']
    assert set(receipt) == {REL + n for n in expected}
    for name in expected:
        raw = (ROOT / REL / name).read_bytes()
        assert raw != old(name)
        with pytest.raises(AssertionError):
            before_wholefoods_all_full_prose(ROOT, REL + name, raw + b'\n')
        if name.endswith('.svg'):
            svg = ET.fromstring(raw)
            assert svg.attrib['aria-labelledby'] == 'title desc'
            assert svg.attrib['role'] == 'img' and svg.attrib['viewBox']
