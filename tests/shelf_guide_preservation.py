"""Permit exactly three hash-pinned guide additions, preserving the old catalog."""
import hashlib
from pathlib import Path
import subprocess
import tempfile

GUIDE = 'guides/shelf-decisions.md'
BEFORE = 'ae3cff87b7c9bd6aea41b06d5a27b0e0d296a7d7a94a3b675d483a4a547a8c72'
SYNTHESIS = '47b62e83244b546f3bd07b7a45ec313c201e7e810105a545364c208671195893'
AFTER = '0a609bf49bd5b243ff523e20ab9a99b97ba515f39e3c729bea604a81bd10b172'
LAYOUT = '2657bd4b13da54ebbd1539a700d2b291be5e8db3976ee4d3b833271c11098184'
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


def verify_preserved_source(root, path, expected, *, patch_bytes=None, dcmp_patch_bytes=None, layout_patch_bytes=None):
    data = (root / path).read_bytes()
    if sha(data) == expected:
        return  # Every unchanged historical source remains valid.
    assert path == GUIDE and expected == BEFORE, path
    assert sha(data) in (SYNTHESIS, AFTER, LAYOUT), 'Guide differs from exact reviewed revisions'
    if sha(data) == LAYOUT:
        layout = layout_patch_bytes if layout_patch_bytes is not None else (root / 'tests/fixtures/shelf-guide-layout-integration-20261030.patch').read_bytes()
        data = reverse_exact(data, layout, LAYOUT_PATCH_SHA, AFTER)
    if sha(data) == AFTER:
        dcmp = dcmp_patch_bytes if dcmp_patch_bytes is not None else (root / 'tests/fixtures/shelf-guide-dcmp-integration-20261030.patch').read_bytes()
        data = reverse_exact(data, dcmp, DCMP_PATCH_SHA, SYNTHESIS)
    patch = patch_bytes if patch_bytes is not None else (root / 'tests/fixtures/shelf-guide-20261029.patch').read_bytes()
    reverse_exact(data, patch, PATCH_SHA, BEFORE)
