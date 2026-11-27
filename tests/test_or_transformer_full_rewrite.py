import hashlib
import json
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_or_transformer_all_full_prose, or_transformer_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'or-transformer-joint-replenishment'


def test_reviewed_or_transformer_document_scope():
    rows = json.loads((ROOT / 'tests/or_transformer_full_rewrite_hashes.json').read_text())['files']
    assert set(rows) == {f'papers/{SLUG}/{name}' for name in ('README.md', 'lab.yaml', 'method.md', 'mapping.md')}
    for path, row in rows.items():
        content = before_or_transformer_all_full_prose(ROOT,path,(ROOT / path).read_bytes())
        hashes = {'sha256': hashlib.sha256(content).hexdigest(),
                  'blob': hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()}
        for alg, sha in hashes.items():
            assert sha == row['after_' + alg]
            assert or_transformer_full_rewrite_hash(ROOT, path, row['before_' + alg], alg) == sha
            with pytest.raises(AssertionError):
                or_transformer_full_rewrite_hash(ROOT, path, sha, alg)
    assert or_transformer_full_rewrite_hash(ROOT, f'papers/{SLUG}/results.json', 'same') == 'same'


def test_reader_summary_and_download_match_including_limits():
    folder = ROOT / 'papers' / SLUG
    lab = yaml.safe_load((folder / 'lab.yaml').read_text())
    download = (folder / 'README.md').read_text()
    for key in ('question', 'summary'):
        assert lab[key] in download
    for value in lab['core_idea'].values():
        assert value in download
    for key, value in lab['sections'].items():
        if key not in ('mapping', 'method'):
            assert value in download
    overview = lab['sections']['overview']
    assert all(x in overview for x in ('50回', '1,024商品', 'PPOより約75%', '実店舗では検証していません'))
    evidence = lab['sections']['evidence']
    assert all(x in evidence for x in ('8回', '19.1%', '6時間', '48時間49分', '内訳は確認できていません'))
    assert 'https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html#timelimit' in evidence
