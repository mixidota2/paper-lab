"""User-supplied SIDScope weights must yield a valid weighted proportion."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'papers/sidscope-diagnostics'
spec = importlib.util.spec_from_file_location('sidscope_input', SOURCE / 'run.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
MAPPING = {'a': [0, 0], 'b': [0, 1], 'c': [1, 0]}


def alignments(pairs):
    result = model.diagnose(MAPPING, pairs)
    json.dumps(result, allow_nan=False)
    return [row['weighted_prefix_alignment'] for row in result['profiles']]


@pytest.mark.parametrize('weight', [-1, -.25, float('nan'), float('inf'),
                                    -float('inf'), True, False, '1', None, [], {}])
@pytest.mark.parametrize('target', ['b', 'not-in-mapping'])
def test_invalid_weight_rejected_even_for_excluded_pair(weight, target):
    with pytest.raises(ValueError, match='weight must be finite and nonnegative'):
        alignments([['a', target, weight]])


@pytest.mark.parametrize('pairs', [None, {}, 'abc', [None], ['abc'], [[]],
                                  [['a', 'b']], [['a', 'b', 1, 2]],
                                  [[[], 'b', 1]], [['a', 2, 1]]])
def test_malformed_pair_structure_rejected(pairs):
    with pytest.raises(ValueError, match='pairs'):
        alignments(pairs)


def test_negative_weights_cannot_create_alignment_greater_than_one():
    with pytest.raises(ValueError):
        alignments([['a', 'b', 2], ['a', 'c', -1]])


@pytest.mark.parametrize('weight', [1, .1, 1e308, 5e-324, 10**400])
def test_large_small_and_integer_weights_have_bounded_exact_ratio(weight):
    assert alignments([['a', 'b', weight], ['a', 'c', weight]]) == [.5, 0]
    assert alignments([['a', 'b', weight], ['a', 'b', weight],
                       ['a', 'c', weight]]) == [2 / 3, 0]


def test_zero_unknown_duplicate_and_self_pairs_keep_existing_semantics():
    assert alignments([]) == [None, None]
    assert alignments([['a', 'b', 0]]) == [None, None]
    assert alignments([['missing', 'b', 100]]) == [None, None]
    assert alignments([['a', 'a', 3], ['a', 'b', 2], ['a', 'c', 1],
                       ['missing', 'b', 100]]) == [5 / 6, .5]
    assert alignments([['a', 'b', 3], ['a', 'b', 2], ['a', 'c', 1]]) == [5 / 6, 0]


def test_default_results_unchanged():
    assert json.dumps(model.compute(), ensure_ascii=False, indent=2) + '\n' == (
        SOURCE / 'results.json').read_text()


@pytest.mark.parametrize('algorithm', ['sha256', 'blob'])
def test_source_revision_accepts_only_pinned_before_and_after(algorithm):
    from prose_preservation import revised_hash
    path = 'papers/sidscope-diagnostics/run.py'
    row = json.loads((ROOT / 'tests/prose_revision_hashes.json').read_text())['files'][path]
    data = (ROOT / path).read_bytes()
    def digest(content):
        if algorithm == 'sha256':
            return hashlib.sha256(content).hexdigest()
        return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
    assert revised_hash(ROOT, path, row['before_' + algorithm], algorithm) == digest(data)
    with pytest.raises(AssertionError):
        revised_hash(ROOT, path, 'unreviewed', algorithm)
    assert row['after_' + algorithm] != digest(data + b'\n# mutation\n')


def standalone(tmp_path):
    script = tmp_path / 'download/run.py'
    script.parent.mkdir()
    shutil.copyfile(SOURCE / 'run.py', script)
    working = tmp_path / 'elsewhere'
    working.mkdir()
    return script, working


def test_cli_standalone_reproduces_default_bytes(tmp_path):
    script, working = standalone(tmp_path)
    result = subprocess.run([sys.executable, '-I', '-S', str(script)],
                            cwd=working, text=True, capture_output=True, check=True)
    assert script.with_name('results.json').read_bytes() == (SOURCE / 'results.json').read_bytes()
    assert json.loads(result.stdout) == model.compute()
    assert not (working / 'results.json').exists()


def test_cli_custom_inputs_large_weights_emit_strict_json(tmp_path):
    script, working = standalone(tmp_path)
    mapping = working / 'mapping.json'
    mapping.write_text(json.dumps(MAPPING))
    (working / 'pairs.json').write_text(json.dumps([['a', 'b', 1e308], ['a', 'c', 1e308]]))
    result = subprocess.run([sys.executable, '-I', '-S', str(script), '--mapping',
                             'mapping.json', '--pairs', 'pairs.json', '--out', 'result.json'],
                            cwd=working, text=True, capture_output=True, check=True)
    text = (working / 'result.json').read_text()
    def reject(value):
        raise AssertionError('nonstandard JSON constant: ' + value)
    data = json.loads(text, parse_constant=reject)
    assert result.stdout == text
    assert data['input_sha256'] == hashlib.sha256(mapping.read_bytes()).hexdigest()
    assert [p['weighted_prefix_alignment'] for p in data['diagnostics']['profiles']] == [.5, 0]


@pytest.mark.parametrize('weight', ['-1', 'NaN', 'Infinity', 'true', '"1"'])
def test_cli_invalid_input_preserves_existing_output(tmp_path, weight):
    script, working = standalone(tmp_path)
    (working / 'mapping.json').write_text(json.dumps(MAPPING))
    (working / 'pairs.json').write_text('[["a", "b", ' + weight + ']]')
    out = working / 'result.json'
    out.write_bytes(b'previous valid result\n')
    result = subprocess.run([sys.executable, '-I', '-S', str(script), '--mapping',
                             'mapping.json', '--pairs', 'pairs.json', '--out', str(out)],
                            cwd=working, text=True, capture_output=True)
    assert result.returncode != 0
    assert result.stdout == ''
    assert 'weight must be finite and nonnegative' in result.stderr
    assert out.read_bytes() == b'previous valid result\n'
