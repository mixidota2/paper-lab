"""Reject source collisions before mutations; destructive compatibility uses disposable fixtures."""
from pathlib import Path
import importlib
import shutil
from unittest.mock import patch

import pytest

m = importlib.import_module('paper_lab.build')
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path):
    root = tmp_path / 'repo'
    (root / 'papers').mkdir(parents=True)
    (root / 'README.md').write_text('sentinel')
    return root


@pytest.mark.parametrize('relative', [
    '.', '..', 'papers', 'papers/nested', 'paper_lab', 'paper_lab/templates',
    'guides', 'guides/nested', 'research-data', 'tests', 'tools', 'skills',
    '.cursor', '.agents', '.github', '.git', 'README.md',
])
def test_source_collisions_never_reach_mutation(project, relative):
    with patch.object(m.shutil, 'rmtree') as delete, patch.object(Path, 'mkdir') as mkdir,          patch.object(Path, 'write_text') as write, patch.object(m.shutil, 'copy2') as copy:
        with pytest.raises(m.LabError, match='Unsafe build output'):
            m.build(root=project, site_dir=project / relative)
        for operation in (delete, mkdir, write, copy):
            operation.assert_not_called()
    assert (project / 'README.md').read_text() == 'sentinel'


def test_external_inputs_both_containment_directions(project, tmp_path):
    papers = tmp_path / 'input' / 'papers'
    papers.mkdir(parents=True)
    for output in (papers, papers.parent, papers / 'new-output'):
        with patch.object(m.shutil, 'rmtree') as delete, patch.object(Path, 'mkdir') as mkdir:
            with pytest.raises(m.LabError):
                m.build(root=project, papers_dir=papers, site_dir=output)
            delete.assert_not_called(); mkdir.assert_not_called()


def test_normalized_and_symlink_aliases(project, tmp_path):
    alias = tmp_path / 'alias'
    alias.symlink_to(project / 'papers', target_is_directory=True)
    root_alias = tmp_path / 'root-alias'
    root_alias.symlink_to(project, target_is_directory=True)
    outputs = [alias, alias / 'child', project / 'site' / '..' / 'guides',
               root_alias, root_alias / 'paper_lab']
    for output in outputs:
        with patch.object(m.shutil, 'rmtree') as delete:
            with pytest.raises(m.LabError):
                m.build(root=root_alias, site_dir=output)
            delete.assert_not_called()


def test_actual_implementation_protected_with_custom_root(project):
    with patch.object(m.shutil, 'rmtree') as delete:
        with pytest.raises(m.LabError):
            m.build(root=project, site_dir=m.TEMPLATES_DIR)
        delete.assert_not_called()


def test_selected_lab_and_file_symlink_targets_protected(project, tmp_path):
    source = tmp_path / 'original'
    source.mkdir()
    (source / 'keep.txt').write_text('original')
    lab = type('LabFixture', (), {'source_dir': source, 'figures': []})()
    with patch.object(m, 'load_all_labs', return_value=[lab]), patch.object(m.shutil, 'rmtree') as delete:
        with pytest.raises(m.LabError):
            m.build(root=project, site_dir=source)
        delete.assert_not_called()
    (project / 'papers' / 'linked.txt').symlink_to(source / 'keep.txt')
    lab.source_dir = project / 'papers'
    with patch.object(m, 'load_all_labs', return_value=[lab]), patch.object(m.shutil, 'rmtree') as delete:
        with pytest.raises(m.LabError):
            m.build(root=project, site_dir=source)
        delete.assert_not_called()
    assert (source / 'keep.txt').read_text() == 'original'


@pytest.mark.parametrize('entry', [m.main, m.cli])
@pytest.mark.parametrize('output', ['.', 'papers', 'guides', '..'])
def test_cli_nonzero_before_deletion(project, monkeypatch, capsys, entry, output):
    monkeypatch.chdir(project)
    args = ['--root', str(project), '--out', output]
    if entry is m.cli:
        args.insert(0, 'build')
    with patch.object(m.shutil, 'rmtree') as delete:
        assert entry(args) == 1
        delete.assert_not_called()
    assert 'Unsafe build output' in capsys.readouterr().err


def test_symlink_loop_is_clear_error(project):
    loop = project / 'loop'
    loop.symlink_to(loop)
    with patch.object(m.shutil, 'rmtree') as delete:
        with pytest.raises(m.LabError, match='Cannot resolve safe build paths'):
            m.build(root=project, site_dir=loop)
        delete.assert_not_called()


def test_normal_default_regeneration_and_external_limited_build(project, tmp_path):
    shutil.copytree(ROOT / 'papers/trace-verifier-brittleness',
                    project / 'papers/trace-verifier-brittleness')
    assert len(m.build(root=project)) == 1
    site = project / 'site'
    first = {p.relative_to(site): p.read_bytes() for p in site.rglob('*') if p.is_file()}
    (site / 'stale.txt').write_text('generated stale file')
    assert len(m.build(root=project)) == 1
    assert {p.relative_to(site): p.read_bytes() for p in site.rglob('*') if p.is_file()} == first
    output = tmp_path / 'dedicated-preview'
    assert len(m.build(root=ROOT, papers_dir=project / 'papers', site_dir=output)) == 1
    assert (output / 'papers/trace-verifier-brittleness.html').is_file()
    (output / 'stale.txt').write_text('generated stale file')
    assert len(m.build(root=ROOT, papers_dir=project / 'papers', site_dir=output)) == 1
    assert not (output / 'stale.txt').exists()
    assert (project / 'papers/trace-verifier-brittleness/results.json').read_bytes() == (
        ROOT / 'papers/trace-verifier-brittleness/results.json').read_bytes()


def test_discovered_external_lab_symlink_rejected_before_deletion(project, tmp_path):
    external = tmp_path / 'external-original'
    shutil.copytree(ROOT / 'papers/trace-verifier-brittleness', external)
    (project / 'papers' / 'trace').symlink_to(external, target_is_directory=True)
    before = {p.relative_to(external): p.read_bytes() for p in external.rglob('*') if p.is_file()}
    with patch.object(m.shutil, 'rmtree') as delete, patch.object(Path, 'mkdir') as mkdir:
        with pytest.raises(m.LabError, match='Unsafe build output'):
            m.build(root=project, site_dir=external)
        delete.assert_not_called(); mkdir.assert_not_called()
    assert {p.relative_to(external): p.read_bytes() for p in external.rglob('*') if p.is_file()} == before


@pytest.mark.parametrize('relative', [
    'templates/style.css', 'templates/library.js', 'templates/interactives.js',
    'templates/index.html', 'templates/paper.html', 'templates/guide.html',
    'templates/teaching.html', 'guides/shelf-decisions.md',
    'guides/forecast-to-replenishment.md', 'guides/replenishment-evidence.yaml',
    'guides/replenishment-filter.js', 'papers/_toy_common.py', 'figure-chain',
])
def test_individual_input_targets_protected(project, tmp_path, relative):
    output = tmp_path / 'output'
    output.mkdir()
    original = output / 'original'
    original.write_text('source sentinel')
    templates = project / 'templates'
    templates.mkdir()
    source = project / 'papers' / 'lab'
    source.mkdir()
    lab = type('LabFixture', (), {'source_dir': source, 'figures': []})()
    if relative == 'figure-chain':
        intermediate = tmp_path / 'figure-directory'
        intermediate.mkdir()
        (source / 'figures').symlink_to(intermediate, target_is_directory=True)
        (intermediate / 'plot.svg').symlink_to(original)
        lab.figures = [{'path': 'figures/plot.svg'}]
    else:
        link = project / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(original)
    with patch.object(m, 'TEMPLATES_DIR', templates), \
         patch.object(m, 'load_all_labs', return_value=[lab]), \
         patch.object(m.shutil, 'rmtree', side_effect=AssertionError('deletion reached')) as delete, \
         patch.object(Path, 'mkdir') as mkdir, patch.object(Path, 'write_text') as write, \
         patch.object(m.shutil, 'copy2') as copy:
        with pytest.raises(m.LabError, match='Unsafe build output'):
            m.build(root=project, site_dir=output)
        for operation in (delete, mkdir, write, copy):
            operation.assert_not_called()
    assert original.read_text() == 'source sentinel'
