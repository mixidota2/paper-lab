from pathlib import Path
import hashlib
import json
import re

import pytest
import yaml

from prose_preservation import before_sparse_inspection_full_prose, sparse_inspection_full_prose_hash

R=Path(__file__).resolve().parents[1]
P='papers/tsfm-sparse-event-ranking/'
C='paper_lab/sparse05.py'


def test_sparse_review_keeps_result_generator_and_render_contracts():
    rows=json.loads((R/'tests/sparse_inspection_full_prose_hashes.json').read_text())['files']
    assert rows.keys()=={C,*(P+n for n in ('README.md','lab.yaml','mapping.md','method.md','results.json','run.py'))}
    def pair(path):
        new=(R/path).read_bytes()
        return before_sparse_inspection_full_prose(R,path,new),new
    for path in rows:
        prior,new=pair(path)
        assert (prior==new)==(path in (P+'run.py',P+'results.json'))
        assert sparse_inspection_full_prose_hash(R,path,hashlib.sha256(prior).hexdigest())==hashlib.sha256(new).hexdigest()
        with pytest.raises(AssertionError):
            before_sparse_inspection_full_prose(R,path,new+b'\n')
    data=json.loads((R/(P+'results.json')).read_bytes())
    assert len(data['distribution_frames'])==99
    assert len(data['reported'])==5 and sum(len(x['rows']) for x in data['scenarios'])==8
    out=[]
    for raw in pair(C):
        ctx={}
        exec(compile(raw,C,'exec'),ctx)
        out.append(ctx['widget'](data))
    a,b=out
    assert a!=b
    for pattern in (r'<script(?: [^>]*)?>(.*?)</script>',r'<(?:input|select|circle|rect|polyline|path)[^>]*>',r'<td>([\d,%.−+]+)</td>'):
        assert re.findall(pattern,a,re.S)==re.findall(pattern,b,re.S)


def test_sparse_top_eight_does_not_change_what_the_paper_comparison_measures():
    sec=yaml.safe_load((R/(P+'lab.yaml')).read_bytes())['sections']
    ov=sec['overview']
    assert all(s in ov for s in ('64時点','5つ','12種類','最大0.031','30組中29組','全体が0を上回りました','LightGBM','この実験では分かりません'))
    assert not any(s in ov for s in ('Lab','教材','4.79'))
    text=sec['evidence']
    assert '| Favorita | 4.34 | 4.80 | 4.79 | 5.01 | 4.98 |' in text
    assert '| M5 | 2.87 | 3.18 | 3.16 | 3.22 | 3.27 |' in text
    assert '実際に8時点を確認したときの平均件数とは言えない' in text
    assert 'NYC taxiのChronos-2で0.057' in text
    assert ov.strip() in (R/(P+'README.md')).read_text()
