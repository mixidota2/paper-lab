"""The CORAL roles follow §4.2 and its two cases remain separate."""
import hashlib
import json
from pathlib import Path

import pytest
from paper_lab.models import load_lab
from prose_preservation import coral_role_clarification_hash

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'papers/coral-meta-config-harness'


def test_exact_published_roles_followup():
    manifest = json.loads((ROOT / 'tests/coral_role_clarification_hashes.json').read_text())
    assert manifest['base'] == 'e5b91de8ab74004c065b9063f4380affc7318fbf'
    assert set(manifest['files']) == {
        (PAPER / name).relative_to(ROOT).as_posix()
        for name in ('README.md', 'method.md', 'lab.yaml')
    }
    for path, row in manifest['files'].items():
        final = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert coral_role_clarification_hash(ROOT, path, row['before_sha256']) == final
        for wrong in ('0' * 64, final):
            with pytest.raises(AssertionError):
                coral_role_clarification_hash(ROOT, path, wrong)


def test_paper_scope_and_method_actors():
    method = (PAPER / 'method.md').read_text()
    assert '分析ツールは観測値' in method and '計算し、要約する' in method
    assert '検索ツールは記憶' in method
    assert 'LLMはその要約と記録を読み、次の設定を提案する' in method
    assert '数値最適化は予算内の設定のうち、提案に最も近いものを返す' in method
    assert '提案がすでに予算内なら、そのまま返す' in method
    assert '動画サービスでは推薦候補を集める予算を経路ごとに' in (PAPER / 'README.md').read_text()
    assert '別のサービスでは、利用者グループごとに' in load_lab(PAPER).sections['overview']
