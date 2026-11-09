"""Original bounded teaching model. Exact tree arithmetic; floating CDF integration."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import isfinite
from decimal import (Decimal, Context, localcontext, ROUND_HALF_EVEN, MIN_EMIN, MAX_EMAX,
                     InvalidOperation, DivisionByZero, Overflow)
from pathlib import Path
import json
from sys import float_info

SLUG = 'inventory-common-threshold-history'

@dataclass(frozen=True)
class Leaf:
    probability: F
    demand: tuple
    signals: tuple

class Tree:
    def __init__(self, leaves, lead=0, holding=(2, 2, 2), backlog=(1, 1, 1)):
        if type(lead) is not int or not 0 <= lead < len(holding) <= 4:
            raise ValueError('bounded horizon/lead required')
        self.T, self.L = len(holding), lead
        self.h, self.p = tuple(map(F, holding)), tuple(map(F, backlog))
        self.leaves = tuple(leaves)
        if len(backlog) != self.T or not 1 <= len(leaves) <= 8:
            raise ValueError('bounded tree required')
        if min(self.h + self.p) < 0 or sum(x.probability for x in leaves) != 1:
            raise ValueError('nonnegative charges and probability sum one required')
        for x in leaves:
            if not isinstance(x.probability, F) or x.probability <= 0:
                raise ValueError('positive rational leaf probabilities required')
            if len(x.demand) != self.T or len(x.signals) != self.T:
                raise ValueError('one demand/signal per period required')
            if any(type(d) is not int or d < 0 for d in x.demand):
                raise ValueError('nonnegative integer demand required')
        self.M = max(sum(x.demand) for x in leaves)
        if self.M > 4:
            raise ValueError('teaching model supports at most four units')

    def history(self, leaf, t):
        if not 1 <= t <= self.T:
            raise ValueError('history period outside horizon')
        if type(leaf) is not int or not 0 <= leaf < len(self.leaves):
            raise ValueError('leaf outside tree')
        x = self.leaves[leaf]
        return x.demand[:t-1], x.signals[:t]

    def group(self, leaf, t):
        key = self.history(leaf, t)
        return tuple(i for i in range(len(self.leaves)) if self.history(i, t) == key)

    def probability_below(self, leaf, observed_t, demand_t, u):
        if not 1 <= demand_t <= self.T or not 1 <= u <= self.M:
            raise ValueError('oracle query outside finite model')
        group = self.group(leaf, observed_t)
        mass = sum(self.leaves[i].probability for i in group)
        return sum((self.leaves[i].probability for i in group
                    if sum(self.leaves[i].demand[:demand_t]) < u), F(0)) / mass

    def charges(self, leaf, s, u, observed_t=None):
        if not 1 <= s <= self.T-self.L:
            raise ValueError('order period outside horizon')
        observed_t = s if observed_t is None else observed_t
        alpha = sum((self.h[r-1] * self.probability_below(leaf, observed_t, r, u)
                     for r in range(s+self.L, self.T+1)), F(0))
        beta = self.p[s+self.L-1] * (1-self.probability_below(leaf, observed_t, s+self.L, u))
        return alpha, beta


def ratio(beta, alpha):
    return beta / alpha if alpha else (float('inf') if beta else F(0))


def cdf(z):
    if z <= 0:
        return 0.0
    if z >= 1:
        return 1.0
    # Fixed correctly-rounded decimal exponential avoids platform libm last-bit differences.
    with localcontext(Context(prec=50, rounding=ROUND_HALF_EVEN,
                              Emin=MIN_EMIN, Emax=MAX_EMAX, capitals=1, clamp=0,
                              traps=[InvalidOperation, DivisionByZero, Overflow])):
        value = Decimal(z.numerator) / Decimal(z.denominator) if isinstance(z, F) else Decimal(z)
        if 0 < value < Decimal('1e-8'):
            # exp(value) - 1 loses all digits when value is smaller than
            # the context precision. Sum expm1 directly instead.
            term = numerator = value
            n = 2
            while True:
                term = term * value / n
                updated = numerator + term
                if updated == numerator:
                    break
                numerator = updated
                n += 1
        else:
            numerator = value.exp() - 1
        return float(numerator / (Decimal(1).exp() - 1))


def fixture(signal=True, lead=0):
    demands = ((0, 0, 2), (0, 1, 0), (1, 0, 2), (1, 1, 0))
    leaves = tuple(Leaf(F(1, 4), d, ('開始', ('多い' if i % 2 == 0 else '少ない') if signal else '未通知', '継続'))
                   for i, d in enumerate(demands))
    return Tree(leaves, lead)


def clocks(tree, leaf, mode='historical'):
    if mode not in ('historical', 'recomputed'):
        raise ValueError('unknown clock mode')
    rows = []
    for t in range(1, tree.T-tree.L+1):
        for u in range(1, tree.M+1):
            alpha, beta = tree.charges(leaf, t, u)
            increments = [ratio(*reversed(tree.charges(leaf, s, u, t if mode == 'recomputed' else s)))
                          for s in range(1, t+1)]
            rows.append(dict(t=t, u=u, alpha=alpha, beta=beta,
                             increment=ratio(beta, alpha), z=sum(increments, F(0))))
    return rows


def simulate(tree, leaf, rho, mode='historical'):
    rho = F(rho)
    if not 0 < rho <= 1:
        raise ValueError('fixed threshold must be in (0,1]')
    stop = {u: tree.T-tree.L+1 for u in range(1, tree.M+1)}
    rows, charged = [], F(0)
    for row in clocks(tree, leaf, mode):
        t, u = row['t'], row['u']
        active = stop[u] > t
        crossing = active and row['z'] >= rho
        if crossing:
            stop[u] = t
        charge = row['alpha'] if crossing else row['beta'] if active else F(0)
        charged += charge
        rows.append(dict(row, action='order' if crossing else 'wait' if active else 'ordered', charge=charge))
    orders = [sum(stop[u] == t for u in stop) if t <= tree.T-tree.L else 0
              for t in range(1, tree.T+1)]
    ledger = []
    cost = F(0)
    for t in range(1, tree.T+1):
        arrived = sum(orders[:max(0, t-tree.L)])
        cumulative = sum(tree.leaves[leaf].demand[:t])
        inventory = arrived-cumulative
        period_cost = tree.h[t-1]*max(inventory, 0) + tree.p[t-1]*max(-inventory, 0)
        cost += period_cost
        ledger.append(dict(t=t, demand=tree.leaves[leaf].demand[t-1], order=orders[t-1],
                           arrived=arrived, inventory=inventory, cost=period_cost))
    initial = sum((tree.p[t-1]*sum(tree.leaves[leaf].demand[:t]) for t in range(1, tree.L+1)), F(0))
    return dict(rows=rows, ledger=ledger, stop=stop, cost=cost, conditional_charge=charged+initial)


def expected(tree, mode='historical'):
    # Policy changes only at these finite clocks. Endpoints have zero CDF mass.
    cuts = sorted({F(0), F(1)} | {r['z'] for i in range(len(tree.leaves))
                  for r in clocks(tree, i, mode) if 0 < r['z'] < 1})
    total, decomposition, intervals = 0.0, 0.0, []
    for lo, hi in zip(cuts, cuts[1:]):
        rho, mass = (lo+hi)/2, cdf(hi)-cdf(lo)
        realized = sum((x.probability*simulate(tree, i, rho, mode)['cost']
                        for i, x in enumerate(tree.leaves)), F(0))
        charge = sum((x.probability*simulate(tree, i, rho, mode)['conditional_charge']
                      for i, x in enumerate(tree.leaves)), F(0))
        total += mass*float(realized)
        decomposition += mass*float(charge)
        intervals.append(dict(lo=lo, hi=hi, mass=mass, cost=realized, charge=charge))
    return dict(cost=total, decomposition=decomposition, intervals=intervals)


def optimum(tree):
    """Independent inventory DP. Actions at a history are common to all its leaves."""
    @lru_cache(None)
    def solve(t, group, orders):
        if t > tree.T:
            return F(0)
        mass = sum(tree.leaves[i].probability for i in group)
        candidates = range(tree.M-sum(orders)+1) if t <= tree.T-tree.L else (0,)
        values = []
        for q in candidates:
            next_orders = orders+(q,)
            arrived = sum(next_orders[:max(0, t-tree.L)])
            immediate = sum((tree.leaves[i].probability * (
                tree.h[t-1]*max(arrived-sum(tree.leaves[i].demand[:t]), 0)
                + tree.p[t-1]*max(sum(tree.leaves[i].demand[:t])-arrived, 0)) for i in group), F(0))/mass
            future = F(0)
            if t < tree.T:
                groups = {}
                for i in group:
                    groups.setdefault(tree.history(i, t+1), []).append(i)
                for subgroup in groups.values():
                    weight = sum(tree.leaves[i].probability for i in subgroup)/mass
                    future += weight*solve(t+1, tuple(subgroup), next_orders)
            values.append(immediate+future)
        return min(values)
    groups = {}
    for i in range(len(tree.leaves)):
        groups.setdefault(tree.history(i, 1), []).append(i)
    return sum((sum(tree.leaves[i].probability for i in group)*solve(1, tuple(group), ())
                for group in groups.values()), F(0))


def tight(epsilon):
    """Float-cost example; epsilon must remain normal after float conversion.

    Subnormal costs have insufficient relative precision for a useful ratio.
    The CDF itself still returns the nearest representable float.
    """
    e = float(epsilon)
    if not isfinite(e) or not 0 < e < .5:
        raise ValueError('tight example requires 0 < epsilon < 0.5')
    if e < float_info.min:
        raise ValueError('tight example requires normal float epsilon >= ' + str(float_info.min))
    probability = cdf(e/(1-e))
    cost = e+(1-2*e)*probability
    return dict(epsilon=e, order_probability=probability, opt=e, cost=cost, ratio=cost/e)


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, float) and not isfinite(value):
        return '∞'
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def generate():
    scenarios = []
    for signal in (True, False):
        for lead in (0, 1):
            tree = fixture(signal, lead)
            cases = []
            for mode in ('historical', 'recomputed'):
                for rho in (F(1, 4), F(1, 2), F(3, 4)):
                    for leaf in range(len(tree.leaves)):
                        cases.append(dict(mode=mode, rho=rho, leaf=leaf, **simulate(tree, leaf, rho, mode)))
            scenarios.append(dict(id=f'{int(signal)}-{lead}', signal=signal, lead=lead,
                                  leaves=[dict(probability=x.probability, demand=x.demand, signals=x.signals) for x in tree.leaves],
                                  opt=optimum(tree), expected=expected(tree), comparison=expected(tree, 'recomputed'), cases=cases))
    return encode(dict(lab_kind='inventory-common-threshold',
                       scope='自作の有限需要木。理論の証明・著者コードの再現・店舗実証ではない。',
                       budget=dict(periods=3, leaves=4, scenarios=4, fixed_cases=96, random_seed=None, monte_carlo=False),
                       verification=dict(mechanism='PARTIAL', production='NOT TESTED', author_code='NOT OBSERVED'),
                       scenarios=scenarios, tight=[tight(e) for e in (.001, .01, .1, .25, .49)]))

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(generate(), ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n', encoding='utf-8')
