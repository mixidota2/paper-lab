import json
import hashlib
from pathlib import Path

import pytest
import yaml

from prose_preservation import before_diff_projection_full_prose, diff_projection_source_version_hash

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'papers/diff-projection-feasible-multi-echelon-inventory'


def test_receipt_matches_only_exact_versioned_files():
    rows = json.loads((ROOT / 'tests/diff_projection_source_version_hashes.json').read_text())['files']
    assert set(rows) == {(DOCS / n).relative_to(ROOT).as_posix() for n in ('lab.yaml', 'README.md', 'mapping.md')}
    for path, row in rows.items():
        data = before_diff_projection_full_prose(ROOT, path, (ROOT / path).read_bytes())
        for algo, digest in [
            ('sha256', hashlib.sha256(data).hexdigest()),
            ('blob', hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()),
        ]:
            assert row['after_' + algo] == digest
            assert diff_projection_source_version_hash(ROOT, path, row['before_' + algo], algo) == digest
            with pytest.raises(AssertionError):
                diff_projection_source_version_hash(ROOT, path, digest, algo)


def test_readable_comparison_keeps_the_original_proof_version():
    lab = yaml.safe_load((DOCS / 'lab.yaml').read_text())
    readme = (DOCS / 'README.md').read_text()
    assert lab['urls']['paper'].endswith('2608.02343')
    assert lab['urls']['pdf'].endswith('2608.02343v1')
    assert lab['source_review']['url'].endswith('2608.02343v1')
    assert all(fig['source'].endswith('2608.02343v1') for fig in lab['teaching_figures'])
    assert '2608.02343v1)' in (DOCS / 'mapping.md').read_text()
    ov, ev = (lab['sections'][k] for k in ('overview', 'evidence'))
    assert ov in readme and ev in readme
    assert all(v in ov for v in ('改訂版', '基本設定で0.9%', '1.8%', '実際の工場で生産計画を変えた結果ではありません'))
    new, legacy = ev.split('以下は[初版の一次資料PDF（v1）]')
    assert all(v in new for v in ('2608.02343v2#S6.SS4', '1,000通り', '99%'))
    assert all(v in legacy for v in ('2608.02343v1)', '0.91%', '22/24', '3.22%／2.54%'))
    assert '3.1%' not in ov
    asml_main, separate_and_ablations = new.split('表5の4設定とは別に', 1)
    assert '3.1%' not in asml_main
    extra, ablation = separate_and_ablations.split('改訂版の表6では', 1)
    assert all(fragment in extra for fragment in ('k−−', '3.1%', '主要4設定の数字ではありません'))
    assert all(fragment in ablation for fragment in ('11.9±2.0%', '35.9±6.9%', '射影の勾配までSTE', '評価時には同じ整数化'))
    old_lab = yaml.safe_load(before_diff_projection_full_prose(
        ROOT, (DOCS / 'lab.yaml').relative_to(ROOT).as_posix(), (DOCS / 'lab.yaml').read_bytes()))
    assert ov == old_lab['sections']['overview']
