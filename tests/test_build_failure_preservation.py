"""Generation/install faults must not discard the last complete local site."""
import importlib
from pathlib import Path
import shutil
from unittest.mock import patch

import pytest

m = importlib.import_module('paper_lab.build')
ROOT = Path(__file__).resolve().parents[1]


def snapshot(root):
    return {str(p.relative_to(root)): ('link', str(p.readlink())) if p.is_symlink()
            else ('file', p.read_bytes()) for p in root.rglob('*') if p.is_file() or p.is_symlink()}


@pytest.fixture
def project(tmp_path):
    root = tmp_path / 'repo'
    shutil.copytree(ROOT / 'papers/trace-verifier-brittleness', root / 'papers/trace-verifier-brittleness')
    site = root / 'site'
    (site / 'nested').mkdir(parents=True)
    (site / 'index.html').write_text('last complete home')
    (site / 'nested/data.bin').write_bytes(b'\0old\xff')
    (site / 'alias').symlink_to('nested/data.bin')
    return root, site


@pytest.mark.parametrize('failure', ['sections', 'copy', 'write', 'interrupt'])
def test_generation_failure_preserves_exact_previous_output(project, failure):
    root, site = project
    before = snapshot(site)
    if failure == 'sections':
        fault = patch.object(m, 'paper_sections', side_effect=RuntimeError('render failed'))
        error = RuntimeError
    elif failure == 'copy':
        fault = patch.object(m.shutil, 'copy2', side_effect=OSError('copy failed'))
        error = OSError
    elif failure == 'write':
        fault = patch.object(Path, 'write_text', side_effect=OSError('write failed'))
        error = OSError
    else:
        fault = patch.object(m, 'paper_sections', side_effect=KeyboardInterrupt())
        error = KeyboardInterrupt
    with fault, pytest.raises(error):
        m.build(root=root)
    assert snapshot(site) == before
    assert not list(root.glob('.site-build-*'))


def test_first_failed_build_does_not_leave_partial_output(project):
    root, site = project
    shutil.rmtree(site)
    with patch.object(m, 'paper_sections', side_effect=RuntimeError('render failed')):
        with pytest.raises(RuntimeError):
            m.build(root=root)
    assert not site.exists()
    assert not list(root.glob('.site-build-*'))


def test_success_replaces_whole_site_and_keeps_reported_destination(project, capsys):
    root, site = project
    assert len(m.build(root=root)) == 1
    first = snapshot(site)
    assert 'nested/data.bin' not in first and 'alias' not in first
    assert first['index.html'][1].startswith(b'<!doctype html>')
    assert not list(root.glob('.site-build-*'))
    assert f'→ {site}' in capsys.readouterr().out
    assert len(m.build(root=root)) == 1
    assert snapshot(site) == first


def test_symlink_output_alias_stays_intact(project, tmp_path):
    root, site = project
    alias = tmp_path / 'site-alias'
    alias.symlink_to(site, target_is_directory=True)
    m.build(root=root, site_dir=alias)
    assert alias.is_symlink() and alias.resolve() == site
    assert (alias / 'index.html').read_bytes() == (site / 'index.html').read_bytes()


def test_output_inside_new_parent_is_supported(project, tmp_path):
    root, _ = project
    site = tmp_path / 'new' / 'nested' / 'preview'
    assert len(m.build(root=root, site_dir=site)) == 1
    assert (site / 'index.html').is_file()
    assert not list(site.parent.glob('.preview-build-*'))


@pytest.mark.parametrize('failure', ['backup', 'install', 'interrupt-install'])
def test_install_failure_keeps_or_restores_previous_output(project, failure):
    root, site = project
    before = snapshot(site)
    rename = Path.rename
    def fail(path, target):
        if (failure == 'backup' and path == site) or (failure != 'backup' and path.name == 'next'):
            if failure == 'interrupt-install':
                raise KeyboardInterrupt()
            raise OSError('rename failed')
        return rename(path, target)
    with patch.object(Path, 'rename', fail):
        with pytest.raises(KeyboardInterrupt if failure == 'interrupt-install' else OSError):
            m.build(root=root)
    assert snapshot(site) == before
    assert not list(root.glob('.site-build-*'))


def test_failed_rollback_retains_recovery_copy_and_names_it(project):
    root, site = project
    before = snapshot(site)
    rename = Path.rename
    def fail(path, target):
        if path.name in {'next', 'previous'}:
            raise OSError('rename failed')
        return rename(path, target)
    with patch.object(Path, 'rename', fail), pytest.raises(m.LabError) as raised:
        m.build(root=root)
    backups = list(root.glob('.site-build-*/previous'))
    assert len(backups) == 1
    assert snapshot(backups[0]) == before
    assert str(backups[0].parent) in str(raised.value)
    assert not site.exists()


def test_cleanup_failure_reports_leftover_without_reversing_success(project, capsys):
    root, site = project
    remove = shutil.rmtree
    def fail(path, *args, **kwargs):
        if Path(path).name.startswith('.site-build-'):
            raise OSError('cleanup failed')
        return remove(path, *args, **kwargs)
    with patch.object(m.shutil, 'rmtree', fail):
        assert len(m.build(root=root)) == 1
    assert (site / 'index.html').read_bytes().startswith(b'<!doctype html>')
    workspaces = list(root.glob('.site-build-*'))
    assert len(workspaces) == 1
    assert str(workspaces[0]) in capsys.readouterr().err
    assert (workspaces[0] / 'previous/index.html').read_text() == 'last complete home'


@pytest.mark.parametrize('where', ['backup', 'install'])
def test_interrupt_after_rename_retains_last_complete_output(project, where):
    root, site = project
    before = snapshot(site)
    rename = Path.rename
    def interrupted(path, target):
        result = rename(path, target)
        if (where == 'backup' and path == site) or (where == 'install' and path.name == 'next'):
            raise KeyboardInterrupt()
        return result
    with patch.object(Path, 'rename', interrupted):
        with pytest.raises(KeyboardInterrupt if where == 'backup' else m.LabError):
            m.build(root=root)
    if where == 'backup':
        assert snapshot(site) == before
        assert not list(root.glob('.site-build-*'))
    else:
        backups = list(root.glob('.site-build-*/previous'))
        assert len(backups) == 1 and snapshot(backups[0]) == before
        assert (site / 'index.html').read_bytes().startswith(b'<!doctype html>')
