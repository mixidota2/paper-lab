"""Execute the actual workflow shell, including its pre-fetch failure path."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import pytest
import yaml

ROOT=Path(__file__).resolve().parents[1]
W=yaml.load((ROOT/'.github/workflows/pages.yml').read_text(),Loader=yaml.BaseLoader)
STEP=next(s for s in W['jobs']['verify-publication']['steps'] if s.get('name')=='Compare the public site with the tested build')
TOKEN='${{ needs.build.outputs.publication_manifest_sha256 }}'


def run_step(tmp_path, digest):
    bindir=tmp_path/'bin';bindir.mkdir()
    (bindir/'python3').symlink_to(sys.executable)
    # Any attempted socket operation aborts before a real network request.
    guard=tmp_path/'guard';guard.mkdir()
    (guard/'sitecustomize.py').write_text("import socket\ndef deny(*a,**k):\n raise RuntimeError('NETWORK IS FORBIDDEN IN THIS TEST')\nsocket.socket.connect=deny\nsocket.create_connection=deny\n")
    env={**os.environ,'PATH':str(bindir)+os.pathsep+os.environ['PATH'],'PYTHONPATH':str(guard)}
    return subprocess.run(['bash','-e','-o','pipefail','-c',STEP['run'].replace(TOKEN,digest)],cwd=tmp_path,env=env,capture_output=True,text=True)


@pytest.mark.parametrize('failure', ('bad_digest','missing_manifest','local_mutation'))
def test_real_input_failure_preserves_diagnostics_without_fetch(tmp_path,failure):
    tools=tmp_path/'tools';tools.mkdir();shutil.copy2(ROOT/'tools/compare_publication.py',tools/'compare_publication.py')
    expected=tmp_path/'publication-expected';site=expected/'site';site.mkdir(parents=True)
    (site/'index.html').write_text('<p>expected</p>')
    from tools import compare_publication as c
    manifest=expected/'publication-manifest.json';digest=c.write_manifest(site,'fixed-test-source',manifest)
    if failure=='bad_digest':digest='0'*64
    elif failure=='missing_manifest':manifest.unlink()
    else:(site/'index.html').write_text('<p>changed</p>')
    cp=run_step(tmp_path,digest)
    assert cp.returncode==2
    diagnostics=tmp_path/'publication-diagnostics'
    assert (diagnostics/'exit-code.txt').read_text().strip()=='2'
    stderr=(diagnostics/'stderr.txt').read_text()
    assert 'NETWORK IS FORBIDDEN' not in stderr
    assert any(s in stderr for s in ('Manifest bytes differ','No such file','Local build differs'))
    assert not (tmp_path/'publication-evidence').exists()


@pytest.mark.parametrize('code', (0,2,3,137))
def test_workflow_keeps_comparator_exit_status_and_both_streams(tmp_path,code):
    tools=tmp_path/'tools';tools.mkdir()
    (tools/'compare_publication.py').write_text(f"import sys\nprint('comparison output')\nprint('comparison diagnostic',file=sys.stderr)\nsys.exit({code})\n")
    cp=run_step(tmp_path,'a'*64)
    assert cp.returncode==code
    d=tmp_path/'publication-diagnostics'
    assert (d/'exit-code.txt').read_text()==str(code)+'\n'
    assert (d/'stdout.txt').read_text()=='comparison output\n'
    assert (d/'stderr.txt').read_text()=='comparison diagnostic\n'
    assert 'comparison output' in cp.stdout and 'comparison diagnostic' in cp.stderr


def test_always_upload_includes_early_failure_diagnostics():
    step=W['jobs']['verify-publication']['steps'][-1]
    assert step['if']=='always()'
    assert step['with']['path'].splitlines()==['publication-evidence/','publication-diagnostics/']
    assert step['with']['if-no-files-found']=='error'
    assert not any('continue-on-error' in s for s in W['jobs']['verify-publication']['steps'])
