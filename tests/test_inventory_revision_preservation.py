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
    # PR20 adds one independently pinned guide revision; preserve all 223
    # pre-existing identities and their canonical digest below.
    assert original.pop('guides/shelf-decisions.md') == {
        'before_blob': '3ced96fe9801736168f6e08a28707390f3325af2',
        'before_sha256': '2657bd4b13da54ebbd1539a700d2b291be5e8db3976ee4d3b833271c11098184',
        'after_blob': 'b5d820348e5418ee871c2139f4df507fb0fa4114',
        'after_sha256': '3fe2874e280af9b28c8ab19b45cb783eb6c9b2ff3aead902ebbbcd3380cf0e9d',
    }
    # Pin the TRACE verification-doc correction separately; all 223 older entries stay unchanged.
    assert original.pop('papers/trace-verifier-brittleness/README.md') == {'before_blob': '02824c799f843bd169933214afa6975fc9accc35', 'before_sha256': '82438c30f9e8197ea73719b81218f4320ae9bb272343e762e013534631b82db9', 'after_blob': '8ce0e685d1b76f1c5afb05bdf2327e74ea563d30', 'after_sha256': 'e96ba74dafbdff21d7d338f3bc45ec0b4d8e4bccf5b4bcea1056ae034743d6e5'}
    # Pin export metadata separately; preserve the original 223-entry digest.
    assert original.pop('papers/assortment-replenishment-hard-constraints/interactive.js') == {'before_blob': '69d549d345ec39b67b9cfac3e78383541f793802', 'before_sha256': '10a7b27ede498378a37297358d9eb5777b629c58280c43d06b3cb2d57d7e4d83', 'after_blob': 'd1bb7bfe6c491a970e99b5836ea08635f2fcce9f', 'after_sha256': 'f8c7275cc9a5a1a8d9120b682ace52588d2a47643174646ca55efde53bc10275'}
    # Pin initial disabled controls separately; the 223-entry digest is unchanged.
    assert original.pop('papers/assortment-replenishment-hard-constraints/interactive.html') == {'before_blob': '95a09aebbff2a91b37a495b91071e7c104550a04', 'before_sha256': 'f4e50095f7639c2fd9f7d5ee2a1caeb0d3d3b9a4d58239b16900effa1f7e8555', 'after_blob': 'da9397274256a953896bc30170ab7f16262ea441', 'after_sha256': '60ec99118451359e3edb6ff3cb6cbfab2499195a1ec749b8d310bb065eacac44'}
    # Pin SIDScope's weight validation separately; keep the 223-entry digest.
    assert original.pop('papers/sidscope-diagnostics/run.py') == {
        'before_blob': '3b4c0a00f4ad9ee4215183775011c7bd8f996eb5',
        'before_sha256': '11474d7c288d6bb3ddd1da533b6ee2e53005a58e52e1d0b8287081e99b2b838a',
        'after_blob': '8f8631c1faf4c3189d98db86ee66ed3c824d5fd1',
        'after_sha256': 'cc473858dd25b9797b3e044ac30b67bb38bfc191461379de4d76997d660171de',
    }
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
