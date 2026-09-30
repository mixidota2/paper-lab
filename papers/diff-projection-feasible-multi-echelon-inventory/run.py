"""Exact two-coordinate QP and paper §4.1.2 integer mapping; no training."""
import itertools
import json
import math
from pathlib import Path


def project(z, cap=6, bound=3):
    # W=diag(1/2,1/2); feasible polygon vertices in counterclockwise order.
    vertices = [(0.,0.),(bound,0.),(bound,cap-bound),(0.,cap)]
    candidates = []
    if feasible(z, cap, bound):
        candidates.append(tuple(z))
    for a,b in zip(vertices,vertices[1:]+vertices[:1]):
        d = [b[i]-a[i] for i in range(2)]
        if not any(d):
            continue
        t = max(0,min(1,sum((z[i]-a[i])*d[i] for i in range(2))/sum(v*v for v in d)))
        candidates.append(tuple(a[i]+t*d[i] for i in range(2)))
    return min(candidates,key=lambda x:objective(x,z))


def feasible(x,cap=6,bound=3):
    return min(x)>=-1e-9 and x[0]<=bound+1e-9 and sum(x)<=cap+1e-9


def objective(x,z):
    return sum((x[i]-z[i])**2 for i in range(2))/4


def integer_map(x,z,cap=6,bound=3):
    floor = [math.floor(v+1e-10) for v in x]
    # KKT stationarity gives M^T lambda = W(z-x), including lower bounds.
    dual_usage = [(z[i]-x[i])/2 for i in range(2)]
    score = [(z[i]-floor[i]-.5)/2-dual_usage[i] for i in range(2)]
    out = floor[:]
    for i in sorted(range(2),key=lambda i:(-score[i],i)):
        candidate=out[:]
        candidate[i]+=1
        if feasible(candidate,cap,bound) and objective(candidate,z)<=objective(out,z)+1e-10:
            out=candidate
    return floor,out


def main():
    cases=[]
    for label,z,j in [('Free',[1.,1.],[[1,0],[0,1]]),('Pinned',[5.,1.],[[0,0],[0,1]]),('Competing',[4.,5.],[[.5,-.5],[-.5,.5]])]:
        x=project(z)
        eps=1e-5
        numeric=[[(project([z[k]+(eps if k==i else 0) for k in range(2)])[r]-project([z[k]-(eps if k==i else 0) for k in range(2)])[r])/(2*eps) for i in range(2)] for r in range(2)]
        err=max(abs(j[r][i]-numeric[r][i]) for r in range(2) for i in range(2))
        assert err<1e-8
        f,im=integer_map(x,z)
        cases.append(dict(label=label,target=z,projected=x,jacobian=j,finite_difference_error=err,floor=f,integer=im))
    samples=0; improved=0; violations=0; max_gap=0
    grid=[(i/10+.013,j/10+.027) for i in range(81) for j in range(81)]
    for z in grid:
        x=project(z); f,im=integer_map(x,z)
        assert objective(im,z)<=objective(f,z)+1e-8
        violations+=not feasible(im)
        improved+=objective(im,z)<objective(f,z)-1e-8
        exact=min(objective(q,z) for q in itertools.product(range(7),repeat=2) if feasible(q))
        max_gap=max(max_gap,objective(im,z)-exact)
        samples+=1
    # Figure 5: generic targets near (1,1), with the sum constraint active.
    reach={'floor':0,'integer_mapping':0}
    for i in range(40):
        for j in range(40):
            z=(1.01+i*.021,1.01+math.sqrt(2)*.007+j*.019)
            f,im=integer_map(project(z,2,2),z,2,2)
            reach['floor']+=f==[1,1]
            reach['integer_mapping']+=im==[1,1]
    assert violations==0 and improved>0 and reach['floor']==0 and reach['integer_mapping']>0
    result=dict(lab01_projection=True,seed=None,scope='2D static geometry; no HDPO, STE training, or inventory simulation',cases=cases,samples=samples,integer_violations=violations,improved_over_floor=improved,max_projection_objective_gap_vs_exact=max_gap,reachability=dict(samples=1600,**reach),paper_evidence={'source':'arXiv:2608.02343v1 Table 4','setting1':{'echelon_DBS':{'holding':218.72,'backorder':68.27},'MSP':{'holding':195.60,'backorder':93.65},'Ours':{'holding':204.21,'backorder':73.53}},'setting2':{'echelon_DBS':{'holding':197.26,'backorder':60.86},'MSP':{'holding':180.89,'backorder':80.65},'Ours':{'holding':189.25,'backorder':62.32}}},verification={'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'})
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['samples','integer_violations','improved_over_floor','max_projection_objective_gap_vs_exact','reachability']},indent=2))

if __name__=='__main__':
    main()
