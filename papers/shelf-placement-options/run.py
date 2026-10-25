"""Two finite full-width geometry toys; no author matheuristic."""
from fractions import Fraction as F
from itertools import product
from math import sqrt
from pathlib import Path
import json

def definition(toy, nu=0, thickness=0, scale=1):
    """Immutable input specification, built independently of candidate rectangles.

    Products: ID, width, allowed (mode, single-face height), facing limit.
    These toys only support one vertical column per product (no rotation).
    """
    nu, thickness, scale = (F(str(x)) for x in (nu, thickness, scale))
    if nu < 0 or thickness < 0 or scale <= 0:
        raise ValueError('余白・板厚は非負、縮尺は正にする')
    if toy == 'a':
        return (2*scale, 8*scale, nu*scale, F(0), 0,
                (('A', 2*scale, (('hang', 3*scale), ('shelf', 2*scale)), 4),))
    if toy == 'b':
        return (4*scale, 9*scale, nu*scale, thickness*scale, 1,
                (('A', 4*scale, (('shelf', 2*scale),), 3),
                 ('B', 4*scale, (('shelf', scale),), 3)))
    raise ValueError('対象は教材AとBのみ')

def check(layout, spec):
    """Exact rational check against separately supplied immutable toy inputs."""
    W,H,nu,t,board_count,products=spec
    errors=[]
    try:
        if tuple(F(str(layout[k])) for k in ('width','height','nu','thickness')) != (W,H,nu,t):
            errors.append('棚・余白の入力不一致')
        boards=[F(str(x)) for x in layout['boards']]
        expected=[x[0] for x in products]
        actual=[x['id'] for x in layout['rects']]
        if sorted(actual)!=sorted(expected) or layout['expected_ids']!=expected:
            errors.append('商品欠落・重複')
        if len(boards)!=board_count or boards!=sorted(set(boards)) or any(y-t<0 or y>H for y in boards):
            errors.append('棚板境界')
        definitions={p[0]:p[1:] for p in products};rects=[]
        for r in layout['rects']:
            if r['id'] not in definitions:
                errors.append('未定義の商品');continue
            width,modes,limit=definitions[r['id']];modes=dict(modes)
            faces=r['faces']
            if isinstance(faces,bool) or not isinstance(faces,int) or not 1<=faces<=limit:
                errors.append(r['id']+':面数');continue
            if r['mode'] not in modes:
                errors.append(r['id']+':未許可の置き方');continue
            x,y,w,h=(F(str(r[k])) for k in ('x','y','w','h'))
            required_h=faces*(modes[r['mode']]+(nu if r['mode']=='hang' else 0))
            if w!=width or h!=required_h or r['max_faces']!=limit:
                errors.append(r['id']+':商品寸法・上限の不一致')
            if w<=0 or h<=0 or x<0 or y<0 or x+w>W or y+h>H:
                errors.append(r['id']+':外枠超過')
            if r['mode']=='shelf':
                if y not in [F(0),*boards]:errors.append(r['id']+':支持面不一致')
                above=[z for z in boards if z>y]
                if above and y+h+nu>min(above)-t:errors.append(r['id']+':棚板下余白不足')
            elif y<(max(boards) if boards else 0):errors.append(r['id']+':吊り区画違反')
            for z in boards:
                if y<z and y+h>z-t:errors.append(r['id']+':棚板との重なり')
            rects.append((x,y,w,h))
        for i,a in enumerate(rects):
            for b in rects[i+1:]:
                x,y,w,h=a;X,Y,Wb,Hb=b
                if not(x+w<=X or X+Wb<=x or y+h<=Y or Y+Hb<=y):errors.append('商品重複')
    except (KeyError,TypeError,ValueError,ZeroDivisionError,OverflowError):
        errors.append('入力形式・有限寸法が不正')
    return dict(feasible=not errors,reasons=errors)

def toy_a(nu=0,beta=.5,scale=1):
    nu=F(str(nu));scale=F(str(scale));rows=[]
    for mode in ['hang','shelf']:
        for b in range(1,5):
            h=(3+nu)*b if mode=='hang' else 2*b
            rect=dict(id='A',x=0,y=0,w=float(2*scale),h=float(h*scale),mode=mode,faces=b,max_faces=4)
            layout=dict(width=float(2*scale),height=float(8*scale),nu=float(nu*scale),thickness=0,boards=[],expected_ids=['A'],rects=[rect])
            test=check(layout, definition('a',nu,scale=scale));rows.append(dict(mode=mode,faces=b,profit=(12 if mode=='hang' else 8)*b**beta,layout=layout,**test))
    feasible=[x for x in rows if x['feasible']];profit=max(x['profit'] for x in feasible);ties=[x for x in feasible if abs(x['profit']-profit)<=1e-10]
    return dict(input=dict(nu=float(nu),beta=beta,scale=float(scale)),candidates=rows,best=ties[0],ties=ties,complete=True)

def toy_b(fixed_y=None,nu=1,thickness=1,scale=1):
    nu,t,scale=map(lambda x:F(str(x)),(nu,thickness,scale));rows=[]
    for a,b,lower in product(range(1,4),range(1,4),['A','B']):
        heights={'A':2*a,'B':b};upper='B' if lower=='A' else 'A'
        y=F(str(fixed_y)) if fixed_y is not None else heights[lower]+nu+t
        rs=[dict(id=i,x=0,y=float((0 if i==lower else y)*scale),w=float(4*scale),h=float(heights[i]*scale),mode='shelf',faces=a if i=='A' else b,max_faces=3) for i in ['A','B']]
        layout=dict(width=float(4*scale),height=float(9*scale),nu=float(nu*scale),thickness=float(t*scale),boards=[float(y*scale)],expected_ids=['A','B'],rects=rs)
        rows.append(dict(faces=[a,b],lower=lower,profit=10*sqrt(a)+8*sqrt(b),layout=layout,**check(layout, definition('b',nu,t,scale))))
    feasible=[r for r in rows if r['feasible']];best=max((r['profit'] for r in feasible),default=None);ties=[r for r in feasible if abs(r['profit']-best)<=1e-10] if best is not None else []
    return dict(input=dict(fixed_y=fixed_y,nu=float(nu),thickness=float(t),scale=float(scale)),candidates=rows,best=ties[0] if ties else None,ties=ties,complete=True)

def pack(rectangles,W,H):
    """Independent integer-coordinate feasibility checker for counterexamples."""
    def search(placed):
        if len(placed)==len(rectangles):return placed
        w,h=rectangles[len(placed)]
        for x,y in product(range(W-w+1),range(H-h+1)):
            if all(x+w<=X or X+ww<=x or y+h<=Y or Y+hh<=y for X,Y,ww,hh in placed):
                found=search(placed+[(x,y,w,h)])
                if found is not None:return found
        return None
    return search([])

def main():
    result=dict(model_version='placement-toy-2',note='独自の全幅商品toy。原論文のベンチマーク・多始点探索・実売上の再現ではない。',
       a=[toy_a(n) for n in [0,1,1.1,5,5.1,6]],b_fixed=toy_b(4),b_free=toy_b(),
       exact_expressions=dict(a_hang='12*sqrt(2)',a_shelf='16',b_fixed='18*sqrt(2)',b_free='10*sqrt(2)+8*sqrt(3)'),
       geometry='rational boundary checks in Python; full-width structure makes minimal support height sufficient',objective_tolerance=1e-10,
       counterexamples=dict(area_but_no_fit=pack([(2,2),(2,2)],3,3),row_failure_witness=pack([(2,3),(2,1),(2,3),(2,1)],4,4)))
    result['improvement_over_fixed']=(result['b_free']['best']['profit']-result['b_fixed']['best']['profit'])/result['b_fixed']['best']['profit']
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'fixed':result['b_fixed']['best']['profit'],'free':result['b_free']['best']['profit'],'improvement':result['improvement_over_fixed']}))
if __name__=='__main__':main()
