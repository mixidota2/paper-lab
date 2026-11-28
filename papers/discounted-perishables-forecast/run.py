"""人工の販売記録で二段階の回帰を試す。実店舗の販売記録は使わない。"""
import json
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import sys

MODES = ("increment", "selection", "substitution")

def rows(mode):
    if mode not in MODES:
        raise ValueError(mode)
    for day, fc, stock, d in product(range(7), (4, 8), (20, 30), (0, 1, 3)):
        baseline = 3 + day + fc + stock // 10
        # 値引き品が売れなかった行には、店がシールを貼らなかった日だけでなく、
        # 店がシールを貼ったものの値引き品が売れなかった日も入る。
        if not d:
            # シールを貼らない行には、総販売数が基準どおりの例と、上下にずれる例を入れる。
            for u in (-1, 0, 1):
                yield day, fc, stock, 0, baseline + u, False, 0
            yield day, fc, stock, 0, baseline, True, 0
            continue
        # 最初の二例で実際に売れた数は同じ。値引きしなかった場合に売れた数だけが違う。
        total_seen = baseline + (0 if mode == "substitution" else d)
        total_without_stickers = baseline + (d if mode == "selection" else 0)
        yield day, fc, stock, d, total_seen, True, total_seen-total_without_stickers

def controls(r):
    return [int(r[0] == day) for day in range(7)] + [r[1], r[2]]

def ols(xs, ys):
    """説明変数の列が線形独立な人工例の正規方程式を、有理数で丸めずに解く。"""
    cols = list(zip(*xs, strict=True))
    dot = lambda a,b: sum(x*y for x,y in zip(a,b,strict=True))
    m = [[Q(dot(a,b)) for b in cols]+[Q(dot(a,ys))] for a in cols]
    for i in range(len(m)):
        j = next(k for k in range(i,len(m)) if m[k][i])
        m[i],m[j] = m[j],m[i]
        p=m[i][i]
        m[i]=[v/p for v in m[i]]
        for k,row in enumerate(m):
            if k!=i:
                c=row[i]
                m[k]=[a-c*b for a,b in zip(row,m[i],strict=True)]
    return [r[-1] for r in m]

def evaluate(mode):
    data = list(rows(mode))
    # 回帰は値引き品が売れたかどうかで行を分ける。シールの有無では分けない。
    base = [r for r in data if not r[3]]
    exposed = [r for r in data if r[3]]
    beta = ols([controls(r) for r in base],[r[4] for r in base])
    design = [controls(r)+[r[3]] for r in exposed]
    residual = [r[4]-sum(a*b for a,b in zip(controls(r),beta,strict=True)) for r in exposed]
    slope = ols(design,residual)[-1]
    total = ols(design,[r[4] for r in exposed])[-1]
    regular = ols(design,[r[4]-r[3] for r in exposed])[-1]
    assert slope == total == 1+regular
    return dict(base_rows=len(base), positive_ds_rows=len(exposed), sticker_only_rows=sum(r[5] for r in base), slope=float(slope), total_slope=float(total), regular_slope=float(regular), mean_residual=float(sum(residual)/len(residual)), true_increment=float(Q(sum(r[-1] for r in exposed),len(exposed))))

def compute():
    return dict(synthetic=True,modes={m:evaluate(m) for m in MODES})

if __name__ == "__main__":
    output=json.dumps(compute(),indent=2)+"\n"
    if len(sys.argv)>1 and sys.argv[1]=="--write":
        Path(__file__).with_name("results.json").write_text(output)
    else:
        print(output,end="")
