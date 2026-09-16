"""Synthetic CSID, prefix beam and GAR probe; no trained model or auction replay."""
import json
import math
from collections import defaultdict
from pathlib import Path


def tokenize(ads, bins=2):
    groups = defaultdict(list)
    for ad in ads:
        groups[ad['key']].append(ad)
    result = {}
    for key, items in groups.items():
        ordered = sorted(items, key=lambda a: (a['bid'], a['id']))
        # Continuous, distinct synthetic bids: rank quantiles have no tie ambiguity.
        for rank, ad in enumerate(ordered):
            result[ad['id']] = (ad['semantic'], key, min(bins - 1, rank * bins // len(ordered)))
    return result


def dispersion(ads, codes):
    groups = defaultdict(list)
    for ad in ads:
        groups[codes[ad['id']]].append(ad['bid'])
    return sum(sum((v-sum(vs)/len(vs))**2 for v in vs) for vs in groups.values())/len(ads)


TREE = {(): [('A', 2., 0.), ('B', 1., 3.), ('X', 3., 4.)],
        ('A',): [('a1', 1., 0.), ('a2', 0., .2)],
        ('B',): [('b1', 1., 3.), ('b2', 0., 2.)],
        ('X',): [('x1', 1., 4.), ('x2', 0., 3.)]}
VALID = {('A','a1'), ('B','b1'), ('B','b2')}


def beam(alpha, width, personalized):
    active = [((), 0.)]
    for depth in range(2):
        expanded = []
        for prefix, score in active:
            choices = [(token, gen+alpha*value) for token, gen, value in TREE[prefix]
                       if not personalized or any(path[:depth+1] == prefix+(token,) for path in VALID)]
            if not choices:
                continue
            maximum = max(v for _,v in choices)
            norm = maximum + math.log(sum(math.exp(v-maximum) for _,v in choices))
            expanded.extend((prefix+(token,), score+v-norm) for token,v in choices)
        active = sorted(expanded, key=lambda a: (-a[1],a[0]))[:width]
    return [{'path': '/'.join(p), 'score': round(s,6), 'valid': p in VALID} for p,s in active]


def compute():
    ads = [{'id':i,'semantic':'game/rpg','key': 'conversion' if i<8 else 'roi',
            'bid': float((i%8)+1)*(1 if i<8 else 10)} for i in range(16)]
    base = {a['id']:a['semantic'] for a in ads}
    frames=[]
    for alpha in (0., .25, .5, 1.):
        for width in (1,2,3):
            for personalized in (False,True):
                candidates=beam(alpha,width,personalized)
                frames.append(dict(alpha=alpha,width=width,personalized=personalized,candidates=candidates,
                                   valid_count=sum(c['valid'] for c in candidates)))
    return {'note':'合成16広告と深さ2の人工木。CSID学習、PPO、GMVの再現ではない。',
            'experiments':[{'name':'属性別の等頻度binで入札の群内分散を比較','dataset':'synthetic distinct bids','n':16,
                           'metrics':{'semantic_only_variance':dispersion(ads,base),
                                      'classify_then_bin_variance':dispersion(ads,tokenize(ads))}}],
            'ads':[{**a,'csid':list(tokenize(ads)[a['id']])} for a in ads], 'frames':frames}


if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(),ensure_ascii=False,indent=2)+'\n')
