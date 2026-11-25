"""Permit hash-pinned guide revisions, preserving the old catalog."""
import gzip
import json
import hashlib
from pathlib import Path
import subprocess
import tempfile

GUIDE = 'guides/shelf-decisions.md'
BEFORE = 'ae3cff87b7c9bd6aea41b06d5a27b0e0d296a7d7a94a3b675d483a4a547a8c72'
SYNTHESIS = '47b62e83244b546f3bd07b7a45ec313c201e7e810105a545364c208671195893'
AFTER = '0a609bf49bd5b243ff523e20ab9a99b97ba515f39e3c729bea604a81bd10b172'
LAYOUT = '2657bd4b13da54ebbd1539a700d2b291be5e8db3976ee4d3b833271c11098184'
WORDING = '3fe2874e280af9b28c8ab19b45cb783eb6c9b2ff3aead902ebbbcd3380cf0e9d'
NOVEMBER = '721e1ec459a12bd8028d203fac055c7e34c0d07a29bbbc08b88d69f760b577ea'
NOVEMBER_PATCH_SHA = '5be9c51055a82e92bb4b2fac4d9fdfaf88a1d799d8bd7713a36610fdcfd49f20'
FULL_REWRITE = '32cbe0d4331f3b1b275565d3e77e7e35348710cf4126053b2fc1da258307d861'
FULL_REWRITE_PATCH_SHA = '6abb2b98f251fe1f3f2b8c1015391b4c22c2758a48492b94c15c15fca9eabd5b'
STREICHER = 'b112c68aeca434d2def88e35ef994e67b8d7c881b5e9572c2b6d9a9fa20b05f9'
STREICHER_PATCH_SHA = '42f8e6aeb91408898cc1994bf4134dc184f3ce76112fb0af5ef246db6c4b268d'
WORDING_OLD = 'Düsterhöftほかは対照群との比較を報告。Fisher・Vaidyanathanのタイヤは一部導入をモデル調整後の売上高で評価。無作為比較ではない'
WORDING_NEW = 'Düsterhöftほかは対照群との比較を報告していますが、割付方法・店舗数・評価期間は未確認です。Fisher・Vaidyanathanのタイヤは一部導入をモデル調整後の売上高で評価しており、こちらは無作為比較ではありません。'
LAYOUT_PATCH_SHA = '652c97a1b34596cfa02e435549c7cfba0cf93aa3277f96fdedfeb252d7385c55'
PATCH_SHA = 'f9c6afccad69567ee76bae880ed1d5e8d8c34ffe952c4634a729f445ef709413'
DCMP_PATCH_SHA = 'e4836201fe2029062bc1b89d55b7dcce19df3065ef1c6b933edf2a82bb1a1020'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def reverse_exact(data, patch, patch_sha, expected):
    assert sha(patch) == patch_sha, 'Reviewed patch changed'
    headers = [line for line in patch.splitlines() if line.startswith((b'--- ', b'+++ '))]
    assert headers == [b'--- a/guides/shelf-decisions.md', b'+++ b/guides/shelf-decisions.md']
    with tempfile.TemporaryDirectory(prefix='shelf-preservation-') as tmp:
        sandbox = Path(tmp)
        target = sandbox / GUIDE
        target.parent.mkdir()
        target.write_bytes(data)
        result = subprocess.run(['git', 'apply', '--reverse', '-'], input=patch,
                                cwd=sandbox, capture_output=True, check=False)
        assert result.returncode == 0, result.stderr.decode(errors='replace')
        files = sorted(str(p.relative_to(sandbox)) for p in sandbox.rglob('*') if p.is_file())
        assert files == [GUIDE], files
        restored = target.read_bytes()
        assert sha(restored) == expected, 'Prior guide was not preserved exactly'
        return restored


def before_asda(data):
    row = json.loads((Path(__file__).parent / 'shelf_asda_hashes.json').read_text())['files'][GUIDE]
    if sha(data) != row['after_sha256']:
        return data
    case, table_row = row['case'].encode(), row['row'].encode()
    assert data.count(case) == data.count(table_row) == 1
    restored = data.replace(case, b'', 1).replace(table_row, b'', 1)
    assert sha(restored) == row['before_sha256']
    return restored


def before_hermans(data):
    data = before_asda(data)
    row = json.loads((Path(__file__).parent / 'shelf_hermans_hashes.json').read_text())
    if sha(data) != row['after_sha256']:
        return data
    section, table_row = row['section'].encode(), row['row'].encode()
    assert data.count(section) == data.count(table_row) == 1
    restored = data.replace(section, b'', 1).replace(table_row, b'', 1)
    assert sha(restored) == row['before_sha256']
    return restored


def before_tsukuba(data):
    data = before_hermans(data)
    receipt = json.loads((Path(__file__).parent / 'shelf_tsukuba_hashes.json').read_text())['files'][GUIDE]
    if sha(data) != receipt['after_sha256']:
        return data
    assert receipt['before_sha256'] == STREICHER
    start = b'<span id="tsukuba-sekisho-shelf-evaluation"></span>'
    following = b'<span id="streicher-aisle-evaluation"></span>'
    row = '| [筑波大学・関彰商事、2026]'.encode()
    assert data.count(start) == data.count(following) == data.count(row) == 1
    first, last = data.index(start), data.index(following)
    assert first < last
    data = data[:first] + data[last:]
    first = data.index(row)
    last = data.index(b'\n', first) + 1
    restored = data[:first] + data[last:]
    assert sha(restored) == STREICHER, 'The new case changed prior guide content'
    return restored


def before_streicher(data, patch_bytes=None):
    data = before_tsukuba(data)
    if sha(data) != STREICHER:
        return data
    patch = patch_bytes if patch_bytes is not None else gzip.decompress((Path(__file__).parent / 'fixtures/shelf-guide-streicher-20261124.patch.gz').read_bytes())
    return reverse_exact(data, patch, STREICHER_PATCH_SHA, FULL_REWRITE)


def before_full_rewrite(data):
    data = before_streicher(data)
    if sha(data) != FULL_REWRITE:
        return data
    patch = gzip.decompress((Path(__file__).parent / 'fixtures/shelf-guide-full-rewrite.patch.gz').read_bytes())
    return reverse_exact(data, patch, FULL_REWRITE_PATCH_SHA, NOVEMBER)


def before_november(data):
    data = before_full_rewrite(data)
    if sha(data) != NOVEMBER:
        return data
    patch = (Path(__file__).parent / 'fixtures/shelf-guide-yomiyasu-20261118.patch').read_bytes()
    return reverse_exact(data, patch, NOVEMBER_PATCH_SHA, WORDING)


def verify_preserved_source(root, path, expected, *, patch_bytes=None, dcmp_patch_bytes=None, layout_patch_bytes=None):
    data = (root / path).read_bytes()
    if sha(data) == expected:
        return  # Every unchanged historical source remains valid.
    assert path == GUIDE and expected == BEFORE, path
    data = before_november(data)
    assert sha(data) in (SYNTHESIS, AFTER, LAYOUT, WORDING), 'Guide differs from exact reviewed revisions'
    if sha(data) == WORDING:
        assert data.count(WORDING_NEW.encode()) == 1
        data = data.replace(WORDING_NEW.encode(), WORDING_OLD.encode())
        assert sha(data) == LAYOUT, 'Wording edit changed unrelated guide content'
    if sha(data) == LAYOUT:
        layout = layout_patch_bytes if layout_patch_bytes is not None else (root / 'tests/fixtures/shelf-guide-layout-integration-20261030.patch').read_bytes()
        data = reverse_exact(data, layout, LAYOUT_PATCH_SHA, AFTER)
    if sha(data) == AFTER:
        dcmp = dcmp_patch_bytes if dcmp_patch_bytes is not None else (root / 'tests/fixtures/shelf-guide-dcmp-integration-20261030.patch').read_bytes()
        data = reverse_exact(data, dcmp, DCMP_PATCH_SHA, SYNTHESIS)
    patch = patch_bytes if patch_bytes is not None else (root / 'tests/fixtures/shelf-guide-20261029.patch').read_bytes()
    reverse_exact(data, patch, PATCH_SHA, BEFORE)
