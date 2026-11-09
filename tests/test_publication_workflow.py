"""Offline checks for the proposed post-deployment comparison wiring."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = yaml.load((ROOT / '.github/workflows/pages.yml').read_text(), Loader=yaml.BaseLoader)


def test_existing_publish_gate_is_preserved_before_manifest_and_upload():
    assert WORKFLOW['on'] == {'push': {'branches': ['main', 'master']}, 'workflow_dispatch': ''}
    steps = WORKFLOW['jobs']['build']['steps']
    test = next(i for i, s in enumerate(steps) if s.get('run') == 'uv run --locked pytest -q -ra --fail-on-skip')
    build = next(i for i, s in enumerate(steps) if s.get('run') == 'uv run --locked paper-lab build')
    manifest = next(i for i, s in enumerate(steps) if s.get('id') == 'publication')
    upload = next(i for i, s in enumerate(steps) if s.get('uses') == 'actions/upload-pages-artifact@v3')
    assert test < build < manifest < upload
    assert steps[0]['with']['fetch-depth'] == '0'
    assert not any('continue-on-error' in s for s in steps)
    assert WORKFLOW['jobs']['deploy']['needs'] == 'build'
    assert WORKFLOW['jobs']['deploy']['steps'] == [{'id': 'deploy', 'uses': 'actions/deploy-pages@v4'}]


def test_expected_artifact_and_job_digest_are_bound_to_same_build():
    build = WORKFLOW['jobs']['build']
    assert build['outputs'] == {'publication_manifest_sha256': '${{ steps.publication.outputs.manifest_sha256 }}'}
    upload = next(s for s in build['steps'] if s.get('uses') == 'actions/upload-artifact@v4')
    assert upload['with']['name'] == 'publication-expected'
    assert upload['with']['path'] == 'site/\npublication-manifest.json\n'
    assert upload['with']['include-hidden-files'] == 'true'
    assert upload['with']['if-no-files-found'] == 'error'


def test_compare_runs_after_deploy_with_read_only_permissions_and_failure_evidence():
    job = WORKFLOW['jobs']['verify-publication']
    assert job['needs'] == ['build', 'deploy']
    assert job['permissions'] == {'contents': 'read'}
    steps = job['steps']
    assert steps[0]['with']['ref'] == '${{ github.sha }}'
    assert steps[1]['uses'] == 'actions/download-artifact@v4'
    assert steps[1]['with'] == {'name': 'publication-expected', 'path': 'publication-expected'}
    command = steps[2]['run']
    assert steps[2]['shell'] == 'bash'
    joined = command.replace('\\\n', '')
    for argument in ('python3 tools/compare_publication.py check', '--site publication-expected/site',
                     '--manifest publication-expected/publication-manifest.json',
                     "--manifest-sha256 '${{ needs.build.outputs.publication_manifest_sha256 }}'",
                     '--out publication-evidence', '--workers 8', '--timeout 20'):
        assert argument in joined
    assert '|| status=$?' in command and 'exit "$status"' in command
    assert steps[-1]['if'] == 'always()'
    assert steps[-1]['with']['path'].splitlines() == ['publication-evidence/', 'publication-diagnostics/']
    assert steps[-1]['with']['if-no-files-found'] == 'error'
    assert int(job['timeout-minutes']) > int(steps[2]['timeout-minutes'])


def test_actual_manifest_shell_writes_verified_job_output(tmp_path):
    site = tmp_path / 'site'
    site.mkdir()
    (site / 'index.html').write_text('<p>Expected site</p>')
    (site / '.nojekyll').write_bytes(b'')
    (tmp_path / 'tools').mkdir()
    shutil.copy2(ROOT / 'tools/compare_publication.py', tmp_path / 'tools/compare_publication.py')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    uv = bin_dir / 'uv'
    uv.write_text('#!/bin/sh\n[ "$1 $2 $3" = "run --locked python" ] || exit 91\nshift 3\nexec ' + str(sys.executable) + ' "$@"\n')
    uv.chmod(0o755)
    step = next(s for s in WORKFLOW['jobs']['build']['steps'] if s.get('id') == 'publication')
    output = tmp_path / 'job-output'
    env = {**os.environ, 'PATH': str(bin_dir) + os.pathsep + os.environ['PATH'], 'GITHUB_SHA': 'a' * 40, 'GITHUB_OUTPUT': str(output)}
    cp = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', step['run']], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    manifest = (tmp_path / 'publication-manifest.json').read_bytes()
    assert output.read_text() == 'manifest_sha256=' + hashlib.sha256(manifest).hexdigest() + '\n'
    parsed = json.loads(manifest)
    assert parsed['source_id'] == 'a' * 40
    assert [f['path'] for f in parsed['files']] == ['.nojekyll', 'index.html']
