"""Self-authored arithmetic examples, not author model training or inference."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import csv
import json
import hashlib
import math


def finite_float(value):
    """Keep zero denominators distinct from float overflow/underflow."""
    if value is None:
        return None
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError('result outside finite float range') from exc
    if not math.isfinite(result) or (value != 0 and result == 0):
        raise ValueError('result outside finite nonzero float range')
    return result


def metrics(actual, forecast, prices, weights, groups):
    n = len(actual)
    if not n or any(len(v) != n for v in (forecast, prices, weights, groups)):
        raise ValueError('equal nonempty vectors required')
    a, f, p, w = [[F(str(x)) for x in v] for v in (actual, forecast, prices, weights)]
    if any(x < 0 for v in (a, f, p, w) for x in v):
        raise ValueError('nonnegative values required')
    nodes = []
    for g in dict.fromkeys(groups):
        ix = [i for i in range(n) if groups[i] == g]
        if len({p[i] for i in ix}) != 1:
            raise ValueError('one historical category price per group required')
        nodes.append((sum(a[i] for i in ix), sum(f[i] for i in ix), p[ix[0]], sum(w[i] for i in ix)))
    den = sum(price*y for y, pred, price, weight in nodes)
    old_den = sum(w)
    corrected = sum(price*abs(y-pred) for y, pred, price, weight in nodes)/den if den else None
    old = sum(weight*abs(y-pred)/max(y,F(1,10**9)) for y,pred,price,weight in nodes)/old_den if old_den else None
    return {'old': finite_float(old), 'corrected': finite_float(corrected)}


def windows(actual, forecast):
    a, f = [F(str(x)) for x in actual], [F(str(x)) for x in forecast]
    if not a or len(a)!=len(f) or any(x<0 for x in a+f):
        raise ValueError('nonnegative equal vectors required')
    ratios = [abs(y-p)/y if y else None for y,p in zip(a,f)]
    return {'mean': None if None in ratios else finite_float(sum(ratios)/len(ratios)),
            'pooled': finite_float(sum(abs(y-p) for y,p in zip(a,f))/sum(a)) if sum(a) else None}


def loss(q,y,r):
    q,y,r=map(lambda x:F(str(x)),(q,y,r))
    if q<0 or y<0 or not 0<r<1:
        raise ValueError('q,y >= 0 and 0 < r < 1 required')
    return finite_float(max(q-y,0)+r/(1-r)*max(y-q,0))


def table_winners(filename, filters, *, raw=None):
    raw = Path(filename).read_bytes() if raw is None else raw
    rows=list(csv.DictReader(raw.decode('utf-8').splitlines()))
    panels={}
    for row in rows:
        if all(row[k]==v for k,v in filters.items()):
            panels.setdefault(row['key'],[]).append((row['model'],F(row['cost'])))
    if len(panels)!=8 or any('favorita' in k for k in panels):
        raise ValueError('expected eight non-Favorita panels')
    winners={k:[m for m,c in v if c==min(x[1] for x in v)] for k,v in sorted(panels.items())}
    counts={}
    for names in winners.values():
        for name in names: counts[name]=counts.get(name,0)+1
    return {'panels':winners,'counts':counts}


SOURCE_SNAPSHOT = 'b7c182730a7744ce655fb467af36b951baca629a'
EXPECTED_BLOBS = {
    'category_cost.csv': 'bd62596c0581216210a75dc32882085447b0633e',
    'decisions.csv': 'ff166093fdb687d9ad44f8a50424482fba16d04c',
}


def input_provenance(filename, expected_blob, *, raw=None):
    raw = Path(filename).read_bytes() if raw is None else raw
    def blob(data):
        return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
    observed = blob(raw)
    stripped = blob(raw[:-1]) if raw.endswith(b'\n') else None
    match = 'exact' if observed == expected_blob else 'one_added_trailing_lf' if stripped == expected_blob else 'unmatched'
    return {'filename': Path(filename).name, 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(), 'git_blob': observed,
            'without_final_lf_git_blob': stripped, 'expected_git_blob': expected_blob,
            'match': match, 'matches_expected_blob': match != 'unmatched'}


def table_results(directory):
    directory = Path(directory)
    raw = {name: (directory/name).read_bytes() for name in EXPECTED_BLOBS}
    inputs = {name: input_provenance(directory/name, expected, raw=raw[name])
              for name, expected in EXPECTED_BLOBS.items()}
    matched = all(item['matches_expected_blob'] for item in inputs.values())
    return {'expected_source_snapshot': SOURCE_SNAPSHOT,
            'source_snapshot': SOURCE_SNAPSHOT if matched else None,
            'source_verification': 'both_expected_blobs_matched' if matched else 'unverified_inputs',
            'verification_scope': ('Input bytes matched expected file blobs, allowing one added trailing LF; repository or experiment reproduction not verified.' if matched else 'Expected blob identifiers are reference only; input origin is unverified.'),
            'inputs': inputs,
            'category': table_winners(directory/'category_cost.csv', {'variant':'dollars'}, raw=raw['category_cost.csv']),
            'replenishment': table_winners(directory/'decisions.csv', {'set':'rolling','decision':'replenish_0.8'}, raw=raw['decisions.csv'])}


def results():
    return {'synthetic':True,'model_version':'retail-grain-1',
            'zero_sales':{name:metrics([100,0],pred,[1,1],[1,1],[0,1]) for name,pred in [('A',[90,1]),('B',[80,0])]},
            'window_order':{name:windows([1,100],pred) for name,pred in [('A',[0,100]),('B',[1,90])]},
            'order_loss':[{'q':q,'y':10,'r':r,'loss':loss(q,10,r)} for r in [.5,.8,.95] for q in [8,10,12]]}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--tables',type=Path);ap.add_argument('--out',type=Path,default=Path(__file__).with_name('results.json'));args=ap.parse_args()
    out=results()
    if args.tables:
        out=table_results(args.tables)
    args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
