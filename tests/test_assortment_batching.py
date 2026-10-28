"""Independent offline equivalence/mutation checks; not Chromium or speed evidence."""
import ast
import copy
from pathlib import Path
import subprocess
import pytest
import review_103 as m
BASE = '4d9c682e23a6a993fc37e89ec0cc400edf63d38c'
ROOT = Path(__file__).resolve().parents[1]


def fixture(second=False):
    r = dict(id='B' if second else 'A', k=2 if second else 1, direct=2., transfer=1., stock=4. if second else 2., required=1., slack=-.5)
    selected = {'rows':[r], 'profit':7. if second else 3.}
    widths = ['60%', '15%' if second else '30%']
    dom = {'rows':[[r['id'],str(r['k']),'2.000','1.000',f"{r['stock']:.3f}",'1.000','0.500']],
           'stocks':[{'text':r['id']+' 棚在庫','stock':[widths[0]],'required':[widths[1]]}],
           'summary':f"profit {selected['profit']:.3f}", 'expectedWidths':[widths]}
    return selected, dom


class Page:
    def __init__(self, dom):self.dom=dom;self.calls=[]
    def evaluate(self, script, widths):
        assert script == m.ASSORTMENT_DOM
        self.calls.append(copy.deepcopy(widths))
        result=copy.deepcopy(self.dom)
        result['expectedWidths']=[[f'{v:g}%' for v in pair] for pair in widths]
        return result


def legacy_assertions(selected, dom):
    # Literal independent transcription of the old assertion contract.
    if not selected:
        assert 'ありません' in dom['summary'];return
    assert len(dom['rows']) == len(selected['rows'])
    for cells,r in zip(dom['rows'],selected['rows']):
        assert cells == [r['id'],str(r['k'])]+[f'{v:.3f}' for v in [r['direct'],r['transfer'],r['stock'],r['required'],max(0,-r['slack'])]]
    active=[r for r in selected['rows'] if r['k']]
    scale=max(1,*[v for r in selected['rows'] for v in [r['stock'],r['required']]])
    assert len(dom['stocks'])==len(active)
    for stock,r in zip(dom['stocks'],active):
        assert stock['text'].startswith(f'{r["id"]} 棚在庫')
        assert len(stock['stock'])==len(stock['required'])==1
        assert stock['stock'][0]==f"{60*r['stock']/scale:g}%"
        assert stock['required'][0]==f"{60*r['required']/scale:g}%"
    assert f'{selected["profit"]:.3f}' in dom['summary']


@pytest.mark.parametrize('mutation',range(14))
def test_equivalence_and_mutations(mutation):
    selected,d=fixture()
    if mutation==1:d['rows'].pop()
    if mutation==2:d['rows'].append(d['rows'][0])
    if mutation==3:d['rows'][0][2]='99.000'
    if mutation==4:d['rows'][0].append('extra')
    if mutation==5:d['stocks'].pop()
    if mutation==6:d['stocks'].append(d['stocks'][0])
    if mutation==7:d['stocks'][0]['text']='wrong 棚在庫'
    if mutation==8:d['stocks'][0]['stock']=[]
    if mutation==9:d['stocks'][0]['required']*=2
    if mutation==10:d['stocks'][0]['stock']=['59%']
    if mutation==11:d['stocks'][0]['required']=['31%']
    if mutation==12:d['summary']='wrong'
    if mutation==13:d['rows'][0]=d['rows'][0][::-1]
    for check in (lambda:legacy_assertions(selected,d),lambda:m.assert_assortment_dom(Page(d),selected)):
        if mutation:
            with pytest.raises(AssertionError):check()
        else:check()


def test_distinct_fresh_states_and_stale_rejection():
    first,a=fixture();second,b=fixture(True)
    page=Page(a);m.assert_assortment_dom(page,first)
    page.dom=b;m.assert_assortment_dom(page,second)
    assert page.calls==[[[60.,30.]],[[60.,15.]]]
    with pytest.raises(AssertionError):m.assert_assortment_dom(Page(a),second)
    with pytest.raises(AssertionError):m.assert_assortment_dom(Page(b),first)


def test_no_selected_and_inactive_rows():
    m.assert_assortment_dom(Page({'summary':'ありません'}),None)
    with pytest.raises(AssertionError):m.assert_assortment_dom(Page({'summary':'wrong'}),None)
    selected,d=fixture();selected['rows'][0]['k']=0;d['rows'][0][1]='0';d['stocks']=[]
    legacy_assertions(selected,d);m.assert_assortment_dom(Page(d),selected)


def baseline(path):return ast.parse(subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT,text=True))


def test_only_assortment_block_changed_and_all_capture_calls_preserved():
    old=baseline('tests/review_103.py');new=ast.parse((ROOT/'tests/review_103.py').read_text())
    def normalize(tree,new=False):
        tree=copy.deepcopy(tree)
        if new:
            tree.body=[n for n in tree.body if not (isinstance(n,ast.FunctionDef) and n.name=='assert_assortment_dom') and not (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ASSORTMENT_DOM' for t in n.targets))]
        # Only old selected assertions versus their single helper call differ.
        class Strip(ast.NodeTransformer):
            def visit_If(self,n):
                if isinstance(n.test,ast.Name) and n.test.id=='selected':return None
                return self.generic_visit(n)
            def visit_Expr(self,n):
                if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='assert_assortment_dom':return None
                return n
        return ast.dump(Strip().visit(tree))
    assert normalize(old)==normalize(new,True)
    def calls(tree):return [ast.dump(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('snapshot','capture')]
    assert calls(old)==calls(new)


def test_capture_instrumentation_preserves_original_ast():
    old=baseline('tests/review_103_capture.py').body[-1]
    new=next(n for n in ast.parse((ROOT/'tests/review_103_capture.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='_capture')
    class Strip(ast.NodeTransformer):
        def visit_With(self,n):
            if isinstance(n.items[0].context_expr,ast.Call) and getattr(n.items[0].context_expr.func,'id',None)=='timed_phase':
                return [self.visit(x) for x in n.body]
            return self.generic_visit(n)
    new=Strip().visit(new);new.name=old.name;new.args=old.args
    assert ast.dump(new)==ast.dump(old)
