"""Independent exhaustive synthetic CASRP oracle, not the paper's heuristic."""
from itertools import product
from pathlib import Path
import json

VERSION='casrp-toy-1'

def case(name):
    configs={
        'T1':([6,5,4],[2,1,1],2,2,5,.8,[(1,0,.8),(2,0,.5)]),
        'T2':([10,6],[1,1],1,1,16,1,[(0,1,1)]),
        'T3':([10,1],[2,1],2,1,10,1,[(1,0,.5)]),
        'T4':([10,1,0],[1,1,1],1,1,10,1,[(0,1,.5),(0,2,.3),(2,1,1)])}
    alpha,prices,K,S,g,f,edges=configs[name];n=len(alpha)
    items=[dict(id=chr(65+i),alpha=a,p=prices[i],c=0,b=1,g=g,K=K,f=f,beta=0,lam=.8 if name=='T4' and i==0 else 1) for i,a in enumerate(alpha)]
    mu=[[0.]*n for _ in items]
    for j,i,v in edges:mu[j][i]=v
    return dict(name=name,items=items,mu=mu,S=S)


def evaluate(data,k):
    xs=data['items'];n=len(xs)
    if len(k)!=n or any(int(v)!=v or not 0<=v<=x['K'] for x,v in zip(xs,k)):raise ValueError('face bounds')
    rows=[];flows=[]
    for j,x in enumerate(xs):
        if not k[j]:
            L=x['lam']*x['alpha']; recovered=0
            for i in range(n):
                amount=L*data['mu'][j][i];recovered+=amount if k[i] else 0
                if amount:flows.append(dict(source=x['id'],target=xs[i]['id'],amount=amount,recovered=bool(k[i])))
            flows.append(dict(source=x['id'],target='未配分',amount=L*(1-sum(data['mu'][j])),recovered=False))
    for i,(x,v) in enumerate(zip(xs,k)):
        direct=x['alpha']*v**x['beta'] if v else 0
        transfer=sum(xs[j]['lam']*xs[j]['alpha']*data['mu'][j][i] for j in range(n) if not k[j]) if v else 0
        D=direct+transfer;q=x['g']*v;required=x['f']*D;slack=q-required
        rows.append(dict(id=x['id'],k=v,direct=direct,transfer=transfer,demand=D,stock=q,required=required,slack=slack,feasible=slack>=-1e-9*max(1,q,required),profit=x['p']*D-x['c'] if v else 0,potential=x['lam']*x['alpha'] if not v else 0,extra=max(0,D-q),ratio=min(1,q/D) if D else None))
    width=sum(x['b']*v for x,v in zip(xs,k));width_ok=width<=data['S']+1e-9
    return dict(k=list(k),rows=rows,flows=flows,width=width,width_ok=width_ok,feasible=width_ok and all(x['feasible'] for x in rows),profit=sum(x['profit'] for x in rows))


def oracle(data,fixed=None):
    best=None;ties=[];count=width_count=feasible_count=0
    for k in product(*(range(x['K']+1) for x in data['items'])):
        if fixed is not None and [bool(x) for x in k]!=fixed:continue
        count+=1;o=evaluate(data,k);width_count+=o['width_ok'];feasible_count+=o['feasible']
        if not o['feasible']:continue
        if best is None or o['profit']>best['profit']+1e-9:best=o;ties=[list(k)]
        elif abs(o['profit']-best['profit'])<=1e-9:ties.append(list(k))
    return dict(best=best,ties=ties,candidates=count,width_feasible=width_count,feasible_count=feasible_count,complete=True)


def experiment(data):
    import copy
    exact=oracle(data);zero=copy.deepcopy(data);zero['mu']=[[0]*len(data['items']) for _ in data['items']]
    unaware=oracle(zero)['best'];returned=evaluate(data,unaware['k']);fixed=oracle(data,[bool(x) for x in unaware['k']])
    optimum=exact['best']['profit']
    gap=(optimum-returned['profit'])/optimum if returned['feasible'] and optimum>0 else None
    return dict(input=data,oracle=exact,no_substitution=unaware,reevaluated=returned,fixed_assortment=fixed,gap=gap)


def main():
    results=dict(model_version=VERSION,note='全て合成値。原論文の近似アルゴリズムや実験表の再現ではない。',cases={n:experiment(case(n)) for n in ('T1','T2','T3','T4')})
    t=case('T3');raw=evaluate(t,[1,0]);results['truncation_counterexample']=dict(original=raw,clipped_demand=10,clipped_profit=20,hard_optimum=1,same_problem=False)
    results['fixed_mu_example']=evaluate(case('T4'),[0,1,0])
    Path(__file__).with_name('results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({n:{'profit':v['oracle']['best']['profit'],'k':v['oracle']['best']['k'],'gap':v['gap']} for n,v in results['cases'].items()}))

if __name__=='__main__':main()
