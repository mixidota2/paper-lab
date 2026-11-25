"""Exact synthetic fixed-shelf-count comparison; no store data."""
from collections import Counter
from itertools import combinations
import json

ROW, COL = 3,4
POS = tuple(range(ROW*COL))
COUNTS = {'A':5, 'B':4, 'C':3}
VALUES = {
    'A': (9, 6, 8, 9, 7, 8, 6, 2, 3, 1, 7, 5),
    'B': (6, 8, 4, 8, 5, 4, 9, 6, 7, 9, 6, 1),
    'C': (3, 2, 3, 7, 8, 2, 2, 7, 5, 5, 8, 8),
}
AB_BONUS = 8
FIXED_CURRENT = tuple('BBBCABACAAAC')
SECOND_START = tuple('AAACABBCABBC')


def neighbors(block_aisle=False):
    for p,q in combinations(POS,2):
        r,c = divmod(p,COL)
        rr,cc = divmod(q,COL)
        if abs(r-rr)+abs(c-cc) != 1:
            continue
        if block_aisle and {c,cc}=={2,3}:
            continue
        yield p,q


EDGES = tuple(neighbors(True))


def valid_counts(x):
    return len(x)==len(POS) and Counter(x)==COUNTS


def connected(x):
    if not valid_counts(x):
        return False
    for cat in COUNTS:
        group = {p for p in POS if x[p]==cat}
        seen = {min(group)}
        while True:
            grown = seen | {q for p,q in EDGES if p in seen and q in group} | {
                p for p,q in EDGES if q in seen and p in group}
            if grown==seen:
                break
            seen=grown
        if seen!=group:
            return False
    return True


def scores(x, bonus=AB_BONUS):
    position = sum(VALUES[cat][i] for i,cat in enumerate(x))
    pair = bonus * sum({x[i],x[j]}=={'A','B'} for i,j in EDGES)
    return position, pair, position+pair


def layouts():
    for a in combinations(POS,COUNTS['A']):
        rem = tuple(sorted(set(POS)-set(a)))
        for b in combinations(rem,COUNTS['B']):
            yield tuple('A' if i in a else 'B' if i in b else 'C' for i in POS)


def optimum(candidates, objective, bonus=AB_BONUS):
    # Stable tie-break: among layouts with an equal score, use lexicographic order.
    return min(candidates,key=lambda x:(-scores(x,bonus)[objective],x))


def greedy():
    remaining = dict(COUNTS)
    chosen = []
    for p in POS:
        cat = min((c for c in COUNTS if remaining[c]),key=lambda c:(-VALUES[c][p],c))
        remaining[cat]-=1
        chosen.append(cat)
    return tuple(chosen)


def swap_search(start):
    x=start
    while True:
        options=[]
        for i,j in combinations(POS,2):
            if x[i]==x[j]:
                continue
            y=list(x)
            y[i],y[j]=y[j],y[i]
            y=tuple(y)
            if connected(y):
                options.append(y)
        best = optimum([x,*options],2)
        if scores(best)[2] <= scores(x)[2]:
            return x
        x=best


def run():
    all_x = list(layouts())
    feasible = [x for x in all_x if connected(x)]
    x_cases = {
        'current': FIXED_CURRENT, 'greedy': greedy(),
        'counts_only': optimum(all_x,0), 'connected_additive': optimum(feasible,0),
        'connected_with_pairs': optimum(feasible,2),
        'swap_from_current': swap_search(FIXED_CURRENT),
        'swap_from_second_start': swap_search(SECOND_START),
    }
    return {'layouts_with_counts':len(all_x),'layouts_connected_no_aisle_crossing':len(feasible),
            'ab_sensitivity': {str(bonus):scores(optimum(feasible,2,bonus),bonus)
                               for bonus in (0,6,7,8)},
            'cases':{name:{'rows':[''.join(x[i:i+COL]) for i in range(0,len(x),COL)],
                           'counts_ok':valid_counts(x),'connected_no_aisle_crossing':connected(x),
                           'position':scores(x)[0],'pair':scores(x)[1],'total':scores(x)[2]}
                     for name,x in x_cases.items()}}


if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
