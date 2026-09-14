"""Synthetic residual quantization versus a numeric final hash; standard library only."""
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
            # Paper Appendix A.3 Eq.34: denominator is occupied SIDs, not items.
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
            # Four ads share content; numeric identity is the only distinguishing input.
            rq.append((q1, q2, q3))
            identity = f'{creative}:{advertiser}'.encode()
            h = int.from_bytes(hashlib.sha256(identity).digest()[:8], 'big') % hash_bins
            hashed.append((q1, q2, h))
    return {'rq': collision_metrics(rq), 'hash': collision_metrics(hashed)}


def main():
    # 4 bins is the matched code-space comparison. Wider hashes are capacity sensitivity.
    runs = {str(b): [experiment(s, b) for s in range(10)] for b in (4, 16, 64)}
    same = runs['4'][0]
    assert same['rq']['collision_pct'] == 100  # identical-content duplicates are inseparable
    assert collision_metrics([(0,), (0,), (1,)])['collision_pct'] == 50
    metrics = {}
    for bins, values in runs.items():
        metrics[f'hash_bins={bins}'] = {
            'rq_collision_pct': round(sum(v['rq']['collision_pct'] for v in values) / 10, 3),
            'hash_collision_pct': round(sum(v['hash']['collision_pct'] for v in values) / 10, 3),
            'code_space': 8 * 4 * int(bins)}
    result = {'note': '合成データ640広告、10 seeds。学習済みUAE・balanced k-means・MGMRの再現ではない。性能と本番はNOT TESTED。',
              'experiments': [{'name': '最終層に数値IDを入れると同一内容を区別できるか', 'metrics': metrics}],
              'runs': runs,
              'definition': 'Col = 1 - singleton occupied SIDs / occupied SIDs; hash collision is still possible'}
    Path(__file__).with_name('results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
