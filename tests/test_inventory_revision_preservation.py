"""The numeric repair changes only two exact content identities, not history."""
from pathlib import Path
import hashlib
import json
import pytest
from prose_preservation import revised_hash

ROOT = Path(__file__).resolve().parents[1]
README = 'papers/inventory-common-threshold-history/README.md'
RUN = 'papers/inventory-common-threshold-history/run.py'
BEFORE = {
    README: {'blob': '73d49ee6ab6ea7e3fbb790397cf58ffafd2561e3',
             'sha256': '60056bef22d1821bbb1d0e394cbe37add8c2619ff1e9e2e3f3dbbe56dbd5baed'},
    RUN: {'blob': 'e0bd34bd4ac3b2139c3b6064f0dfc75e41a5d2e6',
          'sha256': '26426b919007d6badf0f970a7fa470beadd4f4e0646b3ba809b4c2d9084ad80e'},
}

def manifest():
    return json.loads((ROOT/'tests/prose_revision_hashes.json').read_text())

def test_other_223_reviewed_prose_identities_are_unchanged():
    original = {p:r for p,r in manifest()['files'].items() if p not in BEFORE}
    assert len(original) == 223
    canonical = json.dumps(original, sort_keys=True, separators=(',', ':')).encode()
    assert hashlib.sha256(canonical).hexdigest() == '1b67a628b52a403a6e94d9db30ef9888e23f09874a189ad767435b33dfe5c363'

@pytest.mark.parametrize('path', (README, RUN))
@pytest.mark.parametrize('algorithm', ('sha256', 'blob'))
def test_only_exact_old_identities_translate_to_exact_new_bytes(path, algorithm):
    row = manifest()['files'][path]
    assert row['before_'+algorithm] == BEFORE[path][algorithm]
    content = (ROOT/path).read_bytes()
    actual = hashlib.sha256(content).hexdigest() if algorithm == 'sha256' else hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    assert revised_hash(ROOT, path, BEFORE[path][algorithm], algorithm) == actual
    with pytest.raises(AssertionError):
        revised_hash(ROOT, path, '0'*len(actual), algorithm)
    assert revised_hash(ROOT, 'papers/unlisted/run.py', 'unmodified', algorithm) == 'unmodified'
    # A content mutation is never accepted by the fixed replacement identity.
    changed = content + b'\n# changed\n'
    bad = hashlib.sha256(changed).hexdigest() if algorithm == 'sha256' else hashlib.sha1(b'blob '+str(len(changed)).encode()+b'\0'+changed).hexdigest()
    assert row['after_'+algorithm] != bad

def test_inventory_readme_retains_prose_and_states_api_limits():
    text = (ROOT/README).read_text()
    assert '将来の期待費用を遡って求める動的計画法（DP）' in text
    assert 'sys.float_info.min <= epsilon < 0.5' in text
    assert 'この入力制限は`tight()`だけに適用' in text
    assert '呼び出し元のDecimalの桁数・丸め方・指数範囲・例外設定から切り離し' in text
