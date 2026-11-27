"""売れる確率と売れた日の数量を分け、分布の合計と平均を計算する。著者モデルは学習しない。"""
import json
import math
from pathlib import Path


def nb(y, mu, alpha):
    r=1/alpha
    return math.exp(math.lgamma(y+r)-math.lgamma(r)-math.lgamma(y+1)
                    -r*math.log1p(alpha*mu)+y*math.log(alpha*mu/(1+alpha*mu)))


def hurdle(y,p,mu,alpha):
    return 1-p if y==0 else p*nb(y,mu,alpha)/(1-nb(0,mu,alpha))


def experiment():
    frames=[]
    for p,mu in [(.1,2),(.5,2),(.9,2),(.5,6)]:
        alpha=.5
        probs=[hurdle(y,p,mu,alpha) for y in range(1000)]
        mass=sum(probs)
        mean=sum(y*v for y,v in enumerate(probs))
        expected=p*mu/(1-nb(0,mu,alpha))
        assert abs(mass-1)<1e-12 and abs(mean-expected)<1e-10
        frames.append(dict(label=f'p⁺={p}, μ={mu}',p=p,mu=mu,alpha=alpha,
                           zero_hurdle=probs[0],zero_nb=nb(0,mu,alpha),
                           positive_mean=mu/(1-nb(0,mu,alpha)),mean=mean,mass=mass,
                           probabilities=probs[:21],nb_probabilities=[nb(y,mu,alpha) for y in range(21)],tail=1-sum(probs[:21])))
    return dict(lab29='hurdle',frames=frames,
                verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),
                checks={'normalization':'CONFIRMED','positive_mean_correction':'CONFIRMED'},
                note='教材はパラメータを決めて確率を計算した。著者モデルは学習しておらず、M5の予測や店舗の在庫も評価していない。')

if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(experiment(),ensure_ascii=False,indent=2)+'\n')
