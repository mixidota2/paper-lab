"""人工広告で残差量子化と末尾のハッシュを比べる。Python標準ライブラリのみを使う。"""
from collections import Counter
import hashlib
import json
import random
from pathlib import Path


def nearest(value, centers):
    return min(range(len(centers)), key=lambda k: abs(value - centers[k]))


def collision_metrics(codes):
    counts = Counter(codes)
    singletons = sum(n == 1 for n in counts.values())
    return {'items': len(codes), 'unique_sids': len(counts),
            'compression': len(codes) / len(counts),
            # 論文の付録A.3・式34では、広告数ではなく使用したSIDの数を分母にする。
            'collision_pct': 100 * (1 - singletons / len(counts)),
            'items_in_collisions_pct': 100 * sum(n for n in counts.values() if n > 1) / len(codes)}


def experiment(seed, hash_bins):
    rng = random.Random(seed)
    coarse, fine = [float(i) for i in range(8)], [-0.15, -0.05, 0.05, 0.15]
    residual_centers = [-0.03, -0.01, 0.01, 0.03]
    rq, hashed = [], []
    for creative in range(160):
        value = rng.randrange(8) + rng.uniform(-0.19, 0.19)
        q1 = nearest(value, coarse)
        residual = value - coarse[q1]
        q2 = nearest(residual, fine)
        q3 = nearest(residual - fine[q2], residual_centers)
        for advertiser in range(4):
            # 4件の広告は同じ内容を持つ。区別に使える入力は数値IDだけ。
            rq.append((q1, q2, q3))
            identity = f'{creative}:{advertiser}'.encode()
            h = int.from_bytes(hashlib.sha256(identity).digest()[:8], 'big') % hash_bins
            hashed.append((q1, q2, h))
    return {'rq': collision_metrics(rq), 'hash': collision_metrics(hashed)}


def main():
    # 4区間の条件だけ総容量をそろえる。区間を増やす条件では、容量の影響を調べる。
    runs = {str(b): [experiment(s, b) for s in range(10)] for b in (4, 16, 64)}
    same = runs['4'][0]
    assert same['rq']['collision_pct'] == 100  # 内容が同じ広告は区別できない。
    assert collision_metrics([(0,), (0,), (1,)])['collision_pct'] == 50
    metrics = {}
    for bins, values in runs.items():
        metrics[f'hash_bins={bins}'] = {
            'rq_collision_pct': round(sum(v['rq']['collision_pct'] for v in values) / 10, 3),
            'hash_collision_pct': round(sum(v['hash']['collision_pct'] for v in values) / 10, 3),
            'code_space': 8 * 4 * int(bins)}
    result = {'note': 'Labは640件の人工広告を乱数の初期値10通りで比べた。UAE、balanced k-means、MGMRは学習せず、論文の性能や本番の結果は検証していない。',
              'experiments': [{'name': '識別子の末尾で数値IDを使うと、内容が同じ広告を区別できるか', 'metrics': metrics}],
              'runs': runs,
              'definition': 'Colは使用したSIDのうち、複数の広告に割り当てたSIDの割合。ハッシュを使っても衝突する場合がある。'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
