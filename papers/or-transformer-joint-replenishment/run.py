"""Scalar self-attention and exact local gradients, without policy training."""
import itertools
import json
import math
from pathlib import Path


def attention(items):
    tokens = [0.5] + items  # a distinguished global token; no item positions
    output = []
    for query in tokens:
        weights = [math.exp(query * key) for key in tokens]
        output.append(sum(w*v for w,v in zip(weights,tokens))/sum(weights))
    return output[0], output[1:]


def cost(q, opened, setup=3):
    # One item, two periods, zero lead time; unmet demand becomes backlog.
    stock, total = 1. + opened*q, setup*opened
    for demand in [3., 2.]:
        stock -= demand
        total += max(stock,0) + 4*max(-stock,0)
    return total


def derivative(q, opened):
    levels = [1+opened*q-3, 1+opened*q-5]
    return opened * sum(1 if x>0 else -4 for x in levels)


def experiment():
    items=[.2,.9,-.4]
    global_value, quantities=attention(items)
    error=0.
    for perm in itertools.permutations(range(3)):
        g, qs=attention([items[i] for i in perm])
        error=max(error,abs(g-global_value),*(abs(qs[j]-quantities[i]) for j,i in enumerate(perm)))
    assert error < 1e-12
    frames=[]
    for q in [.5,2.5,4.5]:
        eps=1e-5
        finite=(cost(q+eps,1)-cost(q-eps,1))/(2*eps)
        direct=derivative(q,1)
        assert abs(finite-direct)<1e-8
        # Bernoulli logit gradient: E[C(Y)*(Y-p)] = p(1-p)(C1-C0).
        p=.4
        score=p*cost(q,1)*(1-p)+(1-p)*cost(q,0)*(-p)
        exact=p*(1-p)*(cost(q,1)-cost(q,0))
        assert abs(score-exact)<1e-12
        frames.append(dict(label=f'発注量 Q = {q}',q=q,levels=[q-2,q-4],
                           closed_cost=cost(q,0),open_cost=cost(q,1),pathwise=direct,
                           finite_difference=finite,score_gradient=score))
    return dict(lab29='or',frames=frames,permutation=dict(input=items,global_output=global_value,item_outputs=quantities,max_error=error,permutations=6),
                verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),
                checks={'permutation_equivariance':'CONFIRMED','quantity_gradient':'CONFIRMED','opening_score_identity':'CONFIRMED'},
                note='同じ費用関数で解析勾配と中央差分を比較。スカラーattentionは学習済みOR-Transformerではない。')

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(experiment(),ensure_ascii=False,indent=2)+'\n')
