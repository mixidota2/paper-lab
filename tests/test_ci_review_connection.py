"""Local wiring checks; no browser, GitHub write, or workflow dispatch."""
from pathlib import Path
import importlib.util
import os
import subprocess
import sys
import yaml
import pytest

ROOT=Path(__file__).resolve().parents[1]
# BaseLoader avoids YAML 1.1 treating GitHub's `on` key as a boolean.
WORKFLOW=yaml.load((ROOT/'.github/workflows/pr-browser.yml').read_text(),Loader=yaml.BaseLoader)


def test_existing_runner_permissions_and_full_build_order():
    w=WORKFLOW;j=w['jobs']['macos-chrome'];steps=j['steps']
    assert w['on']=={'pull_request':{'branches':['main','master']}}
    assert w['permissions']=={'contents':'read'}
    assert j['runs-on']=='macos-26' and j['timeout-minutes']=='25'
    assert next(s for s in steps if s.get('id')=='browser_review')['timeout-minutes']=='18'
    assert steps[0]['with']['persist-credentials']=='false'
    # The launcher integrity test reads a pinned historical commit with git show.
    assert steps[0]['with']['fetch-depth']=='0'
    run=[s['run'] for s in steps if 'run' in s]
    assert run.index('uv sync --locked --extra dev --python 3.12') < run.index('uv run --locked pytest -q -ra --fail-on-skip') < run.index('uv run --locked paper-lab build')
    pre=next(s['run'] for s in steps if s.get('id')=='preflight')
    browser=next(s['run'] for s in steps if s.get('id')=='browser_review')
    assert '--preflight' in pre and '--run --site site --out browser-review/run' in browser
    assert '--with playwright==1.63.0' in browser
    gate=next(s for s in steps if 'review_103_report.py' in s.get('run',''))
    assert "!cancelled()" in gate['if'] and "steps.browser_review.outcome != 'skipped'" in gate['if']
    assert steps.index(gate)>steps.index(next(s for s in steps if s.get('id')=='browser_review'))
    assert all('continue-on-error' not in s for s in steps)
    upload=steps[-1]
    assert upload['uses']=='actions/upload-artifact@v4'
    assert upload['with']['path']=='browser-review/' and upload['with']['retention-days']=='7'
    assert "!cancelled()" in upload['if'] and "steps.preflight.outcome != 'skipped'" in upload['if']
    assert upload['with']['if-no-files-found']=='warn'


def test_public_preview_is_allowlisted_and_saved_before_browser_guard():
    steps=WORKFLOW['jobs']['macos-chrome']['steps']
    preview=next(s for s in steps if s.get('id')=='build_preview')
    pre=next(s for s in steps if s.get('id')=='preflight')
    browser=next(s for s in steps if s.get('id')=='browser_review')
    assert steps.index(pre)+1 == steps.index(preview)
    assert steps.index(preview)+1 == steps.index(browser)
    assert preview['if']=="${{ success() && steps.preflight.outcome == 'success' }}"
    assert preview['uses']=='actions/upload-artifact@v4'
    assert preview['with']=={
        'name':'public-site-${{ github.sha }}',
        'path':'site/index.html\nsite/assets/\nsite/papers/\nsite/guides/\nsite/figures/\nsite/downloads/\n',
        'include-hidden-files':'false',
        'if-no-files-found':'error',
        'retention-days':'7',
    }
    assert len([s for s in steps if s.get('uses')=='actions/upload-artifact@v4'])==2


@pytest.mark.parametrize('exit_code',[0,1,2])
def test_exact_browser_shell_preserves_exit_and_collects_log(tmp_path,exit_code):
    step=next(s for s in WORKFLOW['jobs']['macos-chrome']['steps'] if s.get('id')=='browser_review')
    bin_dir=tmp_path/'bin';bin_dir.mkdir();stub=bin_dir/'uv'
    stub.write_text('#!/bin/bash\nprintf "injected local wiring test\\n"\nexit '+str(exit_code)+'\n');stub.chmod(0o755)
    (tmp_path/'browser-review').mkdir()
    env={**os.environ,'PATH':str(bin_dir)+os.pathsep+os.environ['PATH']}
    result=subprocess.run(['bash','-e','-c',step['run']],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert result.returncode==exit_code
    assert 'injected local wiring test' in (tmp_path/'browser-review/runtime.log').read_text()


@pytest.mark.parametrize('status,code',[('FAIL',1),('STOPPED',1),('PARTIAL',1),('AUTOMATED PASS / publication pending',0)])
def test_cli_exit_contract_without_browser(tmp_path,monkeypatch,status,code):
    spec=importlib.util.spec_from_file_location('ci_review_entry',ROOT/'tests/review_103.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    site=tmp_path/'site';site.mkdir();out=tmp_path/'review'
    monkeypatch.setattr(sys,'argv',['review_103','--run','--site',str(site),'--out',str(out)])
    monkeypatch.setattr(m,'preflight',lambda _: {'browser':'NOT TESTED'})
    monkeypatch.setattr(m.platform,'system',lambda:'Darwin')
    monkeypatch.setattr(m,'runtime',lambda *args: {'status':status,'automatic_status':'PASS' if status.startswith('AUTOMATED PASS') else 'FAIL'})
    if code:
        with pytest.raises(SystemExit) as e:m.main()
        assert e.value.code==code
    else:m.main()
