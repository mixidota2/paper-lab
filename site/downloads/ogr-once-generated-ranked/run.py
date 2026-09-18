"""OGR teaching calculations; no trained recommender or production timing."""
import hashlib
import json
import math
from pathlib import Path


def schedule(k, d):
    if k < 1 or d < 1:
        raise ValueError('positive slate size and SID depth required')
    # Unit-cost, unlimited parallel SID lanes; planner finishes slot m at t=m.
    lanes = [[m + level for level in range(1, d + 1)] for m in range(1, k + 1)]
    return {'k': k, 'd': d, 'serial': k*d, 'pipeline': max(map(max, lanes)),
            'total_operations': k + k*d, 'ratio': k*d/(k+d), 'lanes': lanes}


def sketch(histories, buckets=16, radius=2):
    """Shared signed hashing of positive TRAINING prefixes, distance weighting."""
    if buckets < 1 or radius < 1:
        raise ValueError('positive sketch dimensions required')
    rows, supporters = {}, {}
    for user, items in histories.items():
        for p, center in enumerate(items):
            rows.setdefault(center, [0.] * buckets)
            supporters.setdefault(center, set())
            for q, neighbor in enumerate(items):
                if not 0 < abs(p-q) <= radius:
                    continue
                digest = hashlib.sha256(('2026:' + str(neighbor)).encode()).digest()
                bucket = int.from_bytes(digest[:4], 'big') % buckets
                sign = 1 if digest[4] % 2 else -1
                rows[center][bucket] += sign / abs(p-q)
                supporters[center].add(user)
    return rows, {i: len(u) for i, u in supporters.items()}


def confidence(users, tau=.5, cap=.35):
    if users < 0 or tau <= 0 or not 0 <= cap <= 1:
        raise ValueError('invalid confidence parameters')
    support = math.log1p(users)
    return cap * support / (support + tau)


def fuse(semantic, collaborative, alpha):
    def unit(v):
        norm = math.sqrt(sum(x*x for x in v))
        return [x/norm for x in v] if norm else [0.] * len(v)
    return ([math.sqrt(1-alpha)*x for x in unit(semantic)] +
            [math.sqrt(alpha)*x for x in unit(collaborative)])


def calibrate(primary, auxiliary):
    """Eq.15 accepts already standardized within-user rewards."""
    kappa = min(abs(primary), abs(auxiliary))/max(abs(primary), abs(auxiliary), 1e-6) if primary*auxiliary > 0 else 0.
    return {'primary': primary, 'auxiliary': auxiliary, 'kappa': kappa,
            'naive_sum': primary+auxiliary, 'calibrated': primary+kappa*auxiliary}


def standardize(values):
    mean = sum(values)/len(values)
    sd = math.sqrt(sum((v-mean)**2 for v in values)/len(values))
    return [(v-mean)/max(sd, 1e-6) for v in values]


def compute():
    histories = {'u1': ['A','B','A'], 'u2': ['A','C'], 'u3': ['D']}
    rows, users = sketch(histories)
    cases = [calibrate(*x) for x in [(1,2),(1,-2),(-1,2),(-1,-2),(0,3),(1,0)]]
    fusion = [{'users': n, 'alpha': confidence(n), 'norm_squared': sum(x*x for x in fuse([3,4],[4,3],confidence(n)))} for n in [0,1,2,10,100]]
    schedules = [schedule(k,d) for k,d in [(5,4),(1,4),(5,1),(10,4)]]
    return {'note': '人工入力と単位時間の依存グラフ。推薦精度・実測速度・学習を再現していない。CountSketch後の学習と量子化は省略。',
            'verification': {'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'},
            'experiments': [
                {'name':'依存経路と総仕事量を分ける', 'metrics': {f"K={x['k']},D={x['d']}": {'逐次':x['serial'],'pipeline':x['pipeline'],'比':round(x['ratio'],4),'OGR総演算':x['total_operations']} for x in schedules}},
                {'name':'同じ標準化報酬に単純和とSPAを適用', 'metrics': {str(i):x for i,x in enumerate(cases)}}],
            'schedules':schedules,'reward_cases':cases,'fusion':fusion,'sketch':rows,'distinct_users':users,
            'checks':{'unit_cost_dependency_depth':'CONFIRMED','primary_sign_preserved':'CONFIRMED','unit_branch_norm':'CONFIRMED','ranking_quality':'NOT TESTED'}}

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(),ensure_ascii=False,indent=2)+'\n')
