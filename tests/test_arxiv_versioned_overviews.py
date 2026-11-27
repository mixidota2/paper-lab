"""Pin existing evidence; report materially new results separately."""
import hashlib
import json
from pathlib import Path
import re

import pytest
import yaml

from prose_preservation import before_tagr_all_full_prose, before_oneranker_full_prose, arxiv_versioned_overview_hash, before_revise_full_rewrite, revise_full_rewrite_hash

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = {'oneranker-ads': ('2603.02999', 'v3'), 'revise-recovery': ('2609.00643', 'v1'),
            'tagr-live-sid': ('2608.24034', 'v1')}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def blob(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()

def test_only_labeled_overviews_and_reference_links_changed():
    files = json.loads((ROOT / 'tests/arxiv_versioned_overview_hashes.json').read_text())['files']
    assert files.keys() == {f'papers/{s}/{n}' for s in VERSIONS for n in ('lab.yaml', 'method.md')}
    for path, row in files.items():
        last = before_tagr_all_full_prose(ROOT, path, (ROOT / path).read_bytes())
        current = before_oneranker_full_prose(ROOT, path, last)
        restored = before_revise_full_rewrite(ROOT, path, current)
        if path.endswith('lab.yaml'):
            field, = re.findall(rb'^  overview: \|-\n(?:    [^\n]+\n|\n(?=    ))+', restored, re.M)
            assert sha(field) == row['overwritten_overview_sha256']
            restored = restored.replace(field, row['prior_overview'].encode())
        for new, old in row['reverse_links'].items():
            assert new.encode() in restored and old.encode() not in restored.replace(new.encode(), b'')
            restored = restored.replace(new.encode(), old.encode())
        for form, hash_ in (('sha256', sha), ('blob', blob)):
            assert hash_(restored) == row['before_' + form]
            pinned = arxiv_versioned_overview_hash(ROOT, path, hash_(restored), form)
            assert pinned == row['after_' + form]
            assert revise_full_rewrite_hash(ROOT, path, pinned, form) == hash_(current)
            with pytest.raises(AssertionError):
                arxiv_versioned_overview_hash(ROOT, path, hash_(restored + b'\n'), form)

@pytest.mark.parametrize('slug,fragments', [
    ('oneranker-ads', ('後段の精密ランキングは変えていません', '1.3427%', '0.7190%', '2%増',
                      '別の比較', 'arxiv.org/html/2603.02999v4#S4.SS4')),
    ('revise-recovery', ('15,939回', '分岐条件', '43.6%', '5.9%', '分散環境での障害復旧')),
    ('tagr-live-sid', ('毎分', 'DLRM', '16.1%', '4,000万人', 'IDの更新だけを試した結果ではありません')),
])
def test_summary_states_comparison_and_prior_source_stays_pinned(slug, fragments):
    arxiv, version = VERSIONS[slug]
    folder = ROOT / 'papers' / slug
    lab = yaml.safe_load((folder / 'lab.yaml').read_text())
    overview = lab['sections']['overview']
    assert all(v in overview for v in fragments)
    assert lab['source_review']['url'].endswith(arxiv + version)
    assert lab['source_review']['pdf_version'] == version
    assert lab['urls']['pdf'].endswith(arxiv + version)
    assert lab['urls']['paper'].endswith(arxiv)
    assert f'arxiv.org/html/{arxiv}{version})' in (folder / 'method.md').read_text()
