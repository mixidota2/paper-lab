"""Keep the STATIC evidence, toy and exact original overview independently checkable."""
from hashlib import sha1, sha256
import json
from pathlib import Path
from prose_preservation import before_static_reader_assets
import re

import pytest
import yaml

from prose_preservation import before_static_constrained_full_rewrite, static_constrained_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
P = 'papers/static-constrained-gr/'


def identity(raw):
    return {'sha256':sha256(raw).hexdigest(),
            'blob':sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()}


def test_static_constrained_four_exact_prose_transitions():
    names=('lab.yaml','README.md','method.md','mapping.md')
    rows=json.loads((ROOT/'tests/static_constrained_full_rewrite_hashes.json').read_text())['files']
    assert set(rows)=={P+n for n in names}
    for path,row in rows.items():
        new=before_static_reader_assets(ROOT,path,(ROOT/path).read_bytes())
        before=before_static_constrained_full_rewrite(ROOT,path,new)
        for alg in ('blob','sha256'):
            old_hash=identity(before)[alg]; new_hash=identity(new)[alg]
            assert row['before_'+alg]==old_hash and row['after_'+alg]==new_hash
            assert static_constrained_full_rewrite_hash(ROOT,path,old_hash,alg)==new_hash
            with pytest.raises(AssertionError):
                static_constrained_full_rewrite_hash(ROOT,path,new_hash,alg)
        with pytest.raises(AssertionError):
            before_static_constrained_full_rewrite(ROOT,path,new+b'\n')
        links=lambda x:set(re.findall(rb'\]\(([^)]*)\)',x))
        assert links(before)==links(new)


def test_static_constrained_primary_results_are_separate_from_lab_replay():
    path=P+'lab.yaml'
    new=before_static_reader_assets(ROOT,path,(ROOT/path).read_bytes())
    before=before_static_constrained_full_rewrite(ROOT,P+'lab.yaml',new)
    original,draft=map(yaml.safe_load,(before,new))
    assert original['sections']['overview']==draft['sections']['overview']
    for key in ('urls','source_review','verification','title','status'):
        assert original[key]==draft[key]
    get_formulas=lambda x:[line['formula'] for line in x['teaching_figures'][0]['steps']]
    assert get_formulas(original)==get_formulas(draft)
    evidence=draft['sections']['evidence']
    for phrase in ('100回','候補制限の追加時間だけ','対象動画の条件で、実験期間ではない','新しい商品が正解の例に限った','70エポック中の最高値','0.42%、候補内の二塔モデルで0.88%、STATICで4.29%'):
        assert phrase in evidence
    assert '動的な更新を今後の課題' in draft['sections']['why_it_might_work']
    for name,sha in {'run.py':'68ad5320fbbccab9fb8cbbd34c98444762aceaab',
                     'results.json':'4320b7251a2b4984480ce98952afb30ff2f1763a'}.items():
        assert identity(before_static_reader_assets(ROOT,P+name,(ROOT/(P+name)).read_bytes()))['blob']==sha
