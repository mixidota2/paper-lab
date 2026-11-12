"""Real module/metadata cycle guards and preservation; no extracted functions."""
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
    shutil.copytree(ROOT / 'papers/trace-verifier-brittleness', root / 'papers/trace-verifier-brittleness')
    (root / 'site').mkdir()
    (root / 'site/old.txt').write_text('previous successful site')
    return root

@pytest.mark.parametrize('relative', [
    'guides/shelf-decisions.md', 'guides/forecast-to-replenishment.md',
    'guides/replenishment-evidence.yaml', 'guides/replenishment-filter.js',
    'papers/_toy_common.py', 'papers/trace-verifier-brittleness/unused.dat',
])
def test_actual_metadata_cycle_rejected_before_staging(project, relative):
    link = project / relative
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(link.name)
    with patch.object(m.tempfile, 'mkdtemp', side_effect=AssertionError('staging reached')) as stage:
        with pytest.raises(m.LabError, match='Cannot resolve safe Lab source paths'):
            m.build(root=project)
        stage.assert_not_called()
    assert (project / 'site/old.txt').read_text() == 'previous successful site'
    assert not list(project.glob('.site-build-*'))

@pytest.mark.parametrize('ancestor', [False, True])
def test_output_cycle_before_staging(project, ancestor):
    (project / 'loop').symlink_to('loop')
    output = project / 'loop' / 'nested' if ancestor else project / 'loop'
    with patch.object(m.tempfile, 'mkdtemp', side_effect=AssertionError('staging reached')) as stage:
        with pytest.raises(m.LabError, match='Cannot resolve safe build paths'):
            m.build(root=project, site_dir=output)
        stage.assert_not_called()
    assert (project / 'site/old.txt').read_text() == 'previous successful site'

def test_real_render_via_valid_and_dangling_alias(project):
    (project / 'alias').symlink_to('papers', target_is_directory=True)
    (project / 'new-site-alias').symlink_to('new-site', target_is_directory=True)
    labs = m.build(root=project, papers_dir=project / 'alias', site_dir=project / 'new-site-alias')
    assert len(labs) == 1
    assert (project / 'new-site/papers/trace-verifier-brittleness.html').is_file()
    assert (project / 'site/old.txt').read_text() == 'previous successful site'

