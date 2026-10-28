"""Assertions on the existing protected browser page; never launches a browser."""
import json


def assert_ledger_geometry(rows):
    """Painted content stays in-cell; numbers and headings remain one line."""
    def check(cell, atomic):
        left, top, right, bottom = cell['box']
        assert right > left and bottom > top
        for x0, y0, x1, y1 in cell['content']:
            assert left - 1 <= x0 <= x1 <= right + 1, 'Ledger content crosses a column boundary'
            assert top - 1 <= y0 <= y1 <= bottom + 1, 'Ledger content crosses a row boundary'
        if atomic:
            assert cell['whiteSpace'] == 'nowrap', 'Ledger numeric/header wrapping enabled'
            assert len(cell['textRects']) == 1, 'Ledger numeric/header text splits across lines'
            x0, y0, x1, y1 = cell['textRects'][0]
            assert x1 > x0 and y1 > y0, 'Ledger text is not painted'
    assert rows
    assert len(rows[0]['headers']) == 6
    for cell in rows[0]['headers']:
        check(cell, True)
    for row in rows:
        assert len(row['geometry']) == 6
        for index, cell in enumerate(row['geometry']):
            check(cell, index != 1)


LEDGER_DOM = r"""(rows)=>{
 const box=e=>{const b=e.getBoundingClientRect();return [b.left,b.top,b.right,b.bottom]};
 const geometry=c=>{
   const content=[...c.querySelectorAll('.tokens,.token')].map(box),textRects=[];
   const walker=document.createTreeWalker(c,NodeFilter.SHOW_TEXT);
   while(walker.nextNode()){
     if(!walker.currentNode.textContent.trim())continue;
     const range=document.createRange();range.selectNodeContents(walker.currentNode);
     for(const b of range.getClientRects())textRects.push([b.left,b.top,b.right,b.bottom]);
   }
   return {box:box(c),content:content.concat(textRects),textRects,whiteSpace:getComputedStyle(c).whiteSpace};
 };
 return rows.map((r,i)=>({cells:[...r.cells].map(c=>c.innerText),
   tokens:[...r.querySelectorAll('.token')].map(e=>({text:e.textContent,c:e.className})),
   geometry:[...r.cells].map(geometry),
   headers:i===0?[...r.closest('table').tHead.rows[0].cells].map(geometry):[]
 }));
}"""


def inspect_deletion(page, source):
    cases=json.loads(source.read_text())['synthetic']
    for case in cases:
        for key,value in case['args'].items():
            page.locator('#deletion-'+key).select_option(str(value))
        out=page.locator('#deletion-output')
        assert out.locator('[data-baseline]').inner_text()==f"{case['baseline']['total']:.2f}"
        assert out.locator('[data-changed]').inner_text()==f"{case['changed']['total']:.2f}"
        assert out.locator('[data-delta]').inner_text()==f"{case['changed']['total']-case['baseline']['total']:.2f}"
        dom=out.locator('tbody tr').evaluate_all(LEDGER_DOM)
        assert_ledger_geometry(dom)
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
