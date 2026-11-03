"""Exact no-observation prefix benchmark; arXiv:2610.40557v1 §3.

No preference estimation, experiments, simulation, or empirical retail effects.
Inputs are exact integers, Fraction values, or rational strings; floats are rejected.
Product indices and cuts are one-based. Smallest optimal cut is our tie rule.
"""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Cut:
    k: int
    exclusion: Fraction
    inclusion: Fraction
    regret: Fraction


@dataclass(frozen=True)
class Benchmark:
    revenues: tuple[Fraction, ...]
    cuts: tuple[Cut, ...]
    optimal_cuts: tuple[int, ...]
    chosen_k: int
    assortment: tuple[int, ...]
    g0: Fraction
    half_revenue_bound: Fraction
    corollary_k: int


def component_a(revenues):
    """Evaluate every k=1..n with r[n+1]=0, retaining every minimizer.

    Scope: finite positive strictly decreasing revenue sequences. The formula
    is the paper's supremum over unknown nonnegative MNL preference weights,
    not regret for any particular preference vector or a finite-grid maximum.
    """
    if not isinstance(revenues, (tuple, list)) or not revenues:
        raise ValueError('revenues must be a nonempty list or tuple')
    values = []
    for value in revenues:
        if isinstance(value, bool) or not isinstance(value, (int, Fraction, str)):
            raise ValueError('use exact int, Fraction, or rational string revenues')
        try:
            values.append(Fraction(value))
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError('invalid rational revenue') from exc
    r = tuple(values)
    if any(x <= 0 for x in r) or any(a <= b for a, b in zip(r, r[1:])):
        raise ValueError('revenues must be positive and strictly decreasing')
    extended = r + (Fraction(0),)
    cuts = tuple(Cut(k, extended[k], r[0]-r[k-1],
                     max(extended[k], r[0]-r[k-1]))
                 for k in range(1, len(r)+1))
    g0 = min(c.regret for c in cuts)
    optimal = tuple(c.k for c in cuts if c.regret == g0)
    chosen = optimal[0]
    bound = r[0]/2
    corollary = max(i for i, value in enumerate(r, 1) if value > bound)
    return Benchmark(r, cuts, optimal, chosen, tuple(range(1, chosen+1)),
                     g0, bound, corollary)

"""Independent exact teaching components; not a paper reproduction.

C enumerates 6**floor(m/2) effective paths, capped at 1296 (m <= 9).
Unused observations are marginalized exactly, not added to the decision.
"""
from fractions import Fraction as F
from itertools import product
from math import comb

PREFIXES = ((1,), (1, 2), (1, 2, 3))
MAX_PATHS = 1296
MAX_B_BUDGET = 128


def parameters(r=(3, 2, 1), v=(1, 1, 1)):
    if len(r) != 3 or len(v) != 3:
        raise ValueError('exactly three products required')
    if any(isinstance(x, bool) or not isinstance(x, (int, F)) for x in (*r, *v)):
        raise ValueError('exact rational inputs required')
    r, v = tuple(map(F, r)), tuple(map(F, v))
    if any(x < 0 for x in (*r, *v)):
        raise ValueError('negative input')
    if r[2] <= 0 or r != (3*r[2], 2*r[2], r[2]):
        raise ValueError('revenues must be (3*a, 2*a, a) for a > 0')
    return r, v


def budget(m, minimum):
    if type(m) is not int or m < minimum:
        raise ValueError('invalid budget')


def probabilities(s, v=(1, 1, 1)):
    _, v = parameters(v=v)
    s = tuple(s)
    if not s or len(set(s)) != len(s) or any(type(i) is not int or i not in (1, 2, 3) for i in s):
        raise ValueError('invalid offered set')
    denominator = 1 + sum(v[i-1] for i in s)
    return {0: 1 / denominator, **{i: v[i-1] / denominator for i in s}}


def revenue(s, r=(3, 2, 1), v=(1, 1, 1)):
    r, v = parameters(r, v)
    return sum((r[i-1] * p for i, p in probabilities(s, v).items() if i), F(0))


def oracle(r=(3, 2, 1), v=(1, 1, 1)):
    return max(revenue(s, r, v) for s in PREFIXES)


def b_choice(m, x):
    budget(m, 1)
    if type(x) is not int or not 0 <= x <= m:
        raise ValueError('invalid count')
    return PREFIXES[0] if 3*x >= 2*m else PREFIXES[1]


def component_b(m, r=(3, 2, 1), v=(1, 1, 1)):
    budget(m, 1)
    if m > MAX_B_BUDGET:
        raise ValueError('exact B budget exceeds 128')
    r, v = parameters(r, v)
    p = probabilities((1,), v)[1]
    expected = sum((F(comb(m, x))*p**x*(1-p)**(m-x)*revenue(b_choice(m, x), r, v)
                    for x in range(m+1)), F(0))
    return oracle(r, v) - expected


def c_choice(first, second, r=(3, 2, 1), threshold=F(1)):
    r, _ = parameters(r)
    if isinstance(threshold, bool) or not isinstance(threshold, (int, F)) or threshold < 0:
        raise ValueError('invalid threshold')
    if not first or len(first) != len(second):
        raise ValueError('equal nonempty groups required')
    for ids, s in zip((first, second), PREFIXES):
        if any(type(i) is not int or i not in (0, *s) for i in ids):
            raise ValueError('observation outside offered set')
    means = tuple(sum((r[i-1] if i else F(0) for i in ids), F(0))/len(ids)
                  for ids in (first, second))
    winner = 0 if means[0] >= means[1] else 1
    return PREFIXES[winner] if means[winner] >= threshold else PREFIXES[2]


def component_c(m, r=(3, 2, 1), v=(1, 1, 1), threshold=F(1)):
    budget(m, 2)
    r, v = parameters(r, v)
    tau = m // 2
    # MAX_PATHS = 6**4; reject before any input-dependent exponentiation.
    if tau > 4:
        raise ValueError('enumeration cap exceeded: floor(m/2) <= 4 required')
    probs = [probabilities(s, v) for s in PREFIXES[:2]]
    distribution = {s: F(0) for s in PREFIXES}
    for first in product(probs[0], repeat=tau):
        for second in product(probs[1], repeat=tau):
            weight = F(1)
            for ids, p in zip((first, second), probs):
                for i in ids:
                    weight *= p[i]
            distribution[c_choice(first, second, r, threshold)] += weight
    expected = sum((p*revenue(s, r, v) for s, p in distribution.items()), F(0))
    return dict(distribution=distribution, expected_revenue=expected,
                expected_regret=oracle(r, v)-expected, total_budget=m,
                effective_budget=2*tau, unused_budget=m-2*tau,
                enumerated_paths=6**tau)


# Integration adapter: bounded UI contract; original A/B/C functions above.
import json
from pathlib import Path
A_INPUTS = ((3,2,1),(2,1),(7,),(9,5,2),(F(3,2),1,F(1,2)),(8,7,6,1))
PREFERENCES = ((1,1,1),(4,1,0),(0,0,4),(0,0,0))
SCALES = (F(1,2),F(1),F(2))

def integrated_case(m, preference, scale):
    if type(m) is not int or not 2 <= m <= 9:
        raise ValueError('m must be an integer from 2 to 9')
    if type(preference) is not int or not 0 <= preference < len(PREFERENCES):
        raise ValueError('unknown preference preset')
    if scale not in SCALES or isinstance(scale,bool):
        raise ValueError('unknown revenue scale')
    v=PREFERENCES[preference];r=tuple(scale*x for x in (3,2,1))
    a=component_a(r);o=oracle(r,v)
    p=probabilities((1,),v)[1]
    bdist={s:F(0) for s in PREFIXES}
    for x in range(m+1):
        bdist[b_choice(m,x)]+=F(comb(m,x))*p**x*(1-p)**(m-x)
    c=component_c(m,r,v,threshold=scale)
    distributions=({s:F(s==a.assortment) for s in PREFIXES},bdist,c['distribution'])
    policies=[]
    for name,dist in zip(('A','B','C'),distributions):
        expected=sum(dist[s]*revenue(s,r,v) for s in PREFIXES)
        policies.append(dict(name=name,distribution=[str(dist[s]) for s in PREFIXES],expected=str(expected),regret=str(o-expected)))
    assert F(policies[1]['regret'])==component_b(m,r,v)
    assert F(policies[2]['regret'])==c['expected_regret']
    return dict(m=m,preference=preference,scale=str(scale),v=list(v),oracle=str(o),policies=policies,
                total=m,effective=c['effective_budget'],unused=c['unused_budget'],paths=c['enumerated_paths'])

def generate():
    acuts=[]
    for r in A_INPUTS:
        a=component_a(r)
        acuts.append(dict(r=[str(x) for x in r],cuts=[dict(k=c.k,exclusion=str(c.exclusion),inclusion=str(c.inclusion),regret=str(c.regret)) for c in a.cuts],
                         optimal=list(a.optimal_cuts),chosen=a.chosen_k,g0=str(a.g0),bound=str(a.half_revenue_bound)))
    return dict(kind='original-exact-finite-enumeration',a=acuts,
                cases=[integrated_case(m,v,s) for s in SCALES for v in range(4) for m in range(2,10)],
                budget=dict(cases=96,max_paths=1296,monte_carlo=False,seed=None),
                limits=['Fixed preference results are not minimax values','No author replication or retail effect'])

if __name__=='__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(generate(),ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
