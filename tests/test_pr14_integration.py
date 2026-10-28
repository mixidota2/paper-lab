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
    expected = expected.replace('107','108')
    expected = expected.replace('from deletion_review import inspect_deletion','from featurearc_review import inspect_featurearc\nfrom deletion_review import inspect_deletion')
    expected = expected.replace('TRACE, EPISEM, DELETION','TRACE, EPISEM, DELETION, FEATUREARC')
    expected = expected.replace("    required += [f'deletion-{w}'","    required += [f'featurearc-{w}' for w in (360,768,1440)]+['nojs-'+FEATUREARC]\n    required += [f'deletion-{w}'")
    expected = expected.replace("sources=['deletion_review.py'","sources=['featurearc_review.py','deletion_review.py'")
    expected = expected.replace('(EPISEM,DELETION)','(EPISEM,DELETION,FEATUREARC)')
    expected = expected.replace('REFS+[WRAPPED,TRACE,EPISEM,DELETION]','REFS+[WRAPPED,TRACE,EPISEM,DELETION,FEATUREARC]')
    expected = expected.replace("'main_105_review_cases.json'","'main_105_review_cases.json','main_107_catalog.json'")
    expected = expected.replace('                for deletion_width in (360,768,1440):',"                for arc_width in (360,768,1440):\n                    ap=browser.new_page(viewport={'width':arc_width,'height':900},device_scale_factor=1)\n                    evidence.page=ap\n                    ap.on('pageerror',lambda error,p=ap:evidence.event('pageerror',error,p))\n                    ap.on('requestfailed',lambda r,p=ap:evidence.event('requestfailed',r.url+' '+str(r.failure),p))\n                    ap.on('console',lambda message,p=ap:evidence.event('console-error',message.text,p) if message.type=='error' else None)\n                    ap.on('response',lambda r,p=ap:evidence.event('http-error',f'{r.status} {r.url}',p) if r.status>=400 and r.url.startswith(base) else None)\n                    def arc_detail():\n                        guard(browser)\n                        assert ap.goto(f'{base}/papers/{FEATUREARC}.html').ok\n                        settled(ap)\n                        assert_paper_heading(ap)\n                        inspect_featurearc(ap,ROOT/'papers'/FEATUREARC/'results.json',lambda name:snapshot(ap,out,f'{FEATUREARC}-{arc_width}-{name}'))\n                        report['action_checks'].append({'slug':FEATUREARC,'width':arc_width,'status':'CONFIRMED: 10 scenarios, 30 stages, independent expectations, chain AND, state, native next/reset and geometry'})\n                    task(f'featurearc-{arc_width}',arc_detail)\n                    ap.close()\n                for deletion_width in (360,768,1440):")
    expected = expected.replace('                    def deletion_fallback():','                    def arc_fallback():\n                        assert nojs.goto(f\'{base}/papers/{FEATUREARC}.html\',wait_until=\'load\').ok\n                        guard(browser)\n                        assert_paper_heading(nojs)\n                        assert nojs.locator(\'#arc-toy noscript\').is_visible()\n                        assert nojs.locator(\'[data-stage-gate]\').inner_text()==\'FAIL\'\n                        assert nojs.locator(\'[data-gate="stage F2P"]\').inner_text()==\'FAIL\'\n                        assert nojs.locator(\'[data-gate="自己テスト"]\').inner_text()==\'PASS\'\n                        assert nojs.evaluate(\'document.documentElement.scrollWidth<=innerWidth\')\n                        nojs.screenshot(path=str(out/f\'{FEATUREARC}-360-nojs.png\'),full_page=False)\n                    task(\'nojs-\'+FEATUREARC,arc_fallback)\n                    def deletion_fallback():')
    # Exact authorized batching transformation; all surrounding runner AST stays pinned.
    expected = replace_once(expected, '                if selected:\n                    rows=page.locator(\'#rows tr\');assert rows.count()==len(selected[\'rows\'])\n                    for i,r in enumerate(selected[\'rows\']):\n                        assert rows.nth(i).locator(\'td\').all_text_contents()==[r[\'id\'],str(r[\'k\'])]+[f\'{v:.3f}\' for v in [r[\'direct\'],r[\'transfer\'],r[\'stock\'],r[\'required\'],max(0,-r[\'slack\'])]]\n                    active=[r for r in selected[\'rows\'] if r[\'k\']]\n                    scale=max(1,*[v for r in selected[\'rows\'] for v in [r[\'stock\'],r[\'required\']]])\n                    stock_rows=page.locator(\'#bars > p\').filter(has_text=\'棚在庫\')\n                    assert stock_rows.count()==len(active)\n                    for j,r in enumerate(active):\n                        stock_row=stock_rows.nth(j)\n                        assert stock_row.inner_text().startswith(f\'{r["id"]} 棚在庫\')\n                        stock_bar=stock_row.locator(\'.bar:not(.required)\')\n                        required_bar=stock_row.locator(\'.bar.required\')\n                        assert stock_bar.count()==required_bar.count()==1\n                        assert_percent_width(stock_bar,60*r[\'stock\']/scale)\n                        assert_percent_width(required_bar,60*r[\'required\']/scale)\n                    assert f\'{selected["profit"]:.3f}\' in page.locator(\'#summary\').inner_text()\n                else:assert \'ありません\' in page.locator(\'#summary\').inner_text()\n', '                assert_assortment_dom(page, selected)\n')
    expected = replace_once(expected, 'def shelf_checks(', 'ASSORTMENT_DOM = """(expectedWidths) => {\n    const serialize = value => {\n        const probe = document.createElement(\'div\');\n        probe.style.width = `${value}%`;\n        return probe.style.width;\n    };\n    return {\n        rows: [...document.querySelectorAll(\'#rows tr\')].map(r => [...r.querySelectorAll(\'td\')].map(c => c.textContent)),\n        stocks: [...document.querySelectorAll(\'#bars > p\')].filter(p => p.textContent.includes(\'棚在庫\')).map(p => ({\n            text: p.innerText,\n            stock: [...p.querySelectorAll(\'.bar:not(.required)\')].map(b => b.style.width),\n            required: [...p.querySelectorAll(\'.bar.required\')].map(b => b.style.width)\n        })),\n        summary: document.querySelector(\'#summary\').innerText,\n        expectedWidths: expectedWidths.map(pair => pair.map(serialize))\n    };\n}"""\n\n\ndef assert_assortment_dom(page, selected):\n    # One fresh DOM read after every state change; expectations remain Python.\n    active = [r for r in selected[\'rows\'] if r[\'k\']] if selected else []\n    scale = max(1, *[v for r in selected[\'rows\'] for v in [r[\'stock\'], r[\'required\']]]) if selected else 1\n    widths = [[60*r[\'stock\']/scale, 60*r[\'required\']/scale] for r in active]\n    assert all(math.isfinite(v) and v >= 0 for pair in widths for v in pair)\n    measured = page.evaluate(ASSORTMENT_DOM, widths)\n    if not selected:\n        assert \'ありません\' in measured[\'summary\']\n        return\n    assert len(measured[\'rows\']) == len(selected[\'rows\'])\n    for cells, r in zip(measured[\'rows\'], selected[\'rows\']):\n        assert cells == [r[\'id\'], str(r[\'k\'])] + [f\'{v:.3f}\' for v in [r[\'direct\'], r[\'transfer\'], r[\'stock\'], r[\'required\'], max(0, -r[\'slack\'])]]\n    assert len(measured[\'stocks\']) == len(active)\n    assert len(measured[\'expectedWidths\']) == len(active)\n    for stock, r, expected in zip(measured[\'stocks\'], active, measured[\'expectedWidths\']):\n        assert stock[\'text\'].startswith(f\'{r["id"]} 棚在庫\')\n        assert len(stock[\'stock\']) == len(stock[\'required\']) == 1\n        assert len(expected) == 2\n        for actual, value in zip([stock[\'stock\'][0], stock[\'required\'][0]], expected):\n            assert value.endswith(\'%\')\n            assert actual == value\n    assert f\'{selected["profit"]:.3f}\' in measured[\'summary\']\n\n\ndef shelf_checks(')
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
