"""Exact source composition: preserve current main plus reviewed deletion checks."""
import ast
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MAIN = 'eb478f2d8cb615681c7fef1510ed8fbb1bbb0a73'
DELETION_HEAD = '3de77f7935af428a93028b17f5c14db7f8adcffb'


def source(ref):
    return subprocess.check_output(['git','show',ref+':tests/review_103.py'],cwd=ROOT,text=True)


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old,new)


def expected_runner():
    expected = source(MAIN)
    deletion = source(DELETION_HEAD)
    # Only catalog cardinality changes, not waits, guards or timeouts.
    expected = expected.replace('106','107')
    expected = replace_once(expected,
        'from catalog_expectations import assert_catalog, WRAPPED, TRACE, EPISEM',
        'from deletion_review import inspect_deletion\nfrom catalog_expectations import assert_catalog, WRAPPED, TRACE, EPISEM, DELETION')
    existing = "    required += [f'episem-{w}' for w in (360,768,1440)]+['nojs-'+EPISEM]\n"
    expected = replace_once(expected,existing,existing+"    required += [f'deletion-{w}' for w in (360,768,1440)]+['nojs-'+DELETION]\n")
    expected = replace_once(expected,"sources=['episem_review.py',","sources=['deletion_review.py','episem_review.py',")
    expected = replace_once(expected,'[[EPISEM,w] for w in (360,768,1440)]','[[slug,w] for slug in (EPISEM,DELETION) for w in (360,768,1440)]')
    expected = replace_once(expected,'REFS+[WRAPPED,TRACE,EPISEM]','REFS+[WRAPPED,TRACE,EPISEM,DELETION]')
    # Insert exact reviewed blocks including all event handlers, guards,
    # screenshots, identity checks and task registration. Nothing is stripped.
    start = deletion.index('                for deletion_width in (360,768,1440):')
    end = deletion.index('                nojs=browser.new_page',start)
    anchor = '                # Reuse the existing guarded browser; no independent launch path.\n                for episem_width in (360,768,1440):\n'
    expected = replace_once(expected,anchor,deletion[start:end]+anchor)
    start = deletion.index('                    def deletion_fallback():')
    end = deletion.index('                    for slug in NOJS:',start)
    anchor = '                    def episem_fallback():\n'
    expected = replace_once(expected,anchor,deletion[start:end]+anchor)
    return expected


def test_whole_current_runner_matches_exact_composition():
    expected = ast.dump(ast.parse(expected_runner()))
    actual = ast.dump(ast.parse((ROOT/'tests/review_103.py').read_text()))
    assert actual == expected


def test_composition_detects_guard_or_capture_removal():
    expected = ast.dump(ast.parse(expected_runner()))
    current = (ROOT/'tests/review_103.py').read_text()
    for original, mutation in [('                        guard(browser)','                        pass'),('snapshot(dp,out,', 'print(dp,out,')]:
        assert original in current
        assert ast.dump(ast.parse(current.replace(original,mutation))) != expected
