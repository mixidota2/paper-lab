"""Assertions on the existing protected browser page; never launches a browser."""
import json


def inspect_deletion(page, source):
    cases=json.loads(source.read_text())['synthetic']
    for case in cases:
        for key,value in case['args'].items():
            page.locator('#deletion-'+key).select_option(str(value))
        out=page.locator('#deletion-output')
        assert out.locator('[data-baseline]').inner_text()==f"{case['baseline']['total']:.2f}"
        assert out.locator('[data-changed]').inner_text()==f"{case['changed']['total']:.2f}"
        assert out.locator('[data-delta]').inner_text()==f"{case['changed']['total']-case['baseline']['total']:.2f}"
        dom=out.locator('tbody tr').evaluate_all('(rows)=>rows.map(r=>({cells:[...r.cells].map(c=>c.innerText),tokens:[...r.querySelectorAll(".token")].map(e=>({text:e.textContent,c:e.className}))}))')
        assert len(dom)==len(case['changed']['rows'])
        previous=[]
        for row,actual in zip(case['changed']['rows'],dom):
            assert actual['cells'][2:]==[f"{row['n']} / {row['c']}",str(row['rebilled']),str(row['output']),f"{row['cost']:.2f}"]
            assert len(actual['tokens'])==row['n']
            for j,(token,shown) in enumerate(zip(row['prompt'],actual['tokens'])):
                assert shown['text']==('↓' if j==row['first_changed'] else '')+token
                expected='cached' if j<row['c'] else 'rebilled' if token in previous[row['c']:] else 'new'
                assert shown['c']=='token '+expected
            previous=row['prompt']
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    # Native button activation, with focus checked; no select keyboard claim.
    reset=page.locator('#deletion-reset');reset.focus()
    assert reset.evaluate('e=>e===document.activeElement')
    reset.press('Enter')
    assert [page.locator('#deletion-'+x).input_value() for x in ['discount','position','timing','retrieval']]==['0.9','1','4','0']
    initial=next(c for c in cases if c['args']==dict(discount=.9,position=1,timing=4,retrieval=0))
    assert page.locator('[data-changed]').inner_text()==f"{initial['changed']['total']:.2f}"
