"""Call probe(page) with an already authorized, protected browser page.
No browser launch or protection bypass; not part of the 382-case manifest.
"""
from review_measurements import assert_percent_width


def probe(page):
    page.set_content('<div id="bar"></div>')
    bar=page.locator('#bar');results=[]
    for expected in [0, 100/3, 60*7/13, 100*.767038/.980009, 100]:
        bar.evaluate('(e,v)=>e.style.width=`${v}%`',expected)
        assert_percent_width(bar,expected)
        results.append({'expected':expected,'serialized':bar.evaluate('(e)=>e.style.width')})
        for mutation in [f'{expected+.001}%',f'{expected}px','',f'{expected+1}%']:
            bar.evaluate('(e,v)=>e.style.width=v',mutation)
            try:assert_percent_width(bar,expected)
            except AssertionError:pass
            else:raise AssertionError(f'Width mutation accepted: {expected!r} -> {mutation!r}')
    # A demand-only paragraph must never substitute for a stock row.
    page.set_content('<div id="bars"><p>A 棚在庫1 <span class="bar"></span>'
                     '<br>A 必要量2 <span class="bar required"></span></p>'
                     '<p>A：1 ＋ 2<br><span class="bar"></span>'
                     '<span class="bar required"></span></p></div>')
    rows=page.locator('#bars > p').filter(has_text='棚在庫')
    assert rows.count()==1
    assert rows.first.locator('.bar:not(.required)').count()==1
    assert rows.first.locator('.bar.required').count()==1
    rows.first.evaluate('(e)=>e.remove()')
    assert rows.count()==0  # Remaining demand bars cannot hide a missing stock row.
    return results
