"""CVPMとHaMRの計算を試し、二次元のベクトルを角度で動かす。RQ-VAEは学習しない。"""
import json
import math
from pathlib import Path


def qualified(i, j, ids, batch):
    positive = (i < batch and j == i + batch) or (j < batch and i == j + batch)
    return ids[i] != ids[j] and not positive


def pair_loss(hamming, distance, valid=True, radius=2, full=.8, partial=.5):
    if not valid or hamming > radius:
        return 0.0
    return max(0.0, (full if hamming == 0 else partial) - distance)


def hamr(ids, sids, angles, batch, masked=True, radius=2):
    groups = {'full': [], 'partial': []}
    pairs = []
    for i in range(len(ids)):
        for j in range(len(ids)):
            valid = qualified(i, j, ids, batch) if masked else i != j
            h = sum(a != b for a, b in zip(sids[i], sids[j]))
            d = 1 - math.cos(angles[i] - angles[j])
            loss = pair_loss(h, d, valid, radius)
            if valid and h <= radius:
                groups['full' if h == 0 else 'partial'].append(loss)
            if i < j:
                pairs.append(dict(i=i, j=j, hamming=h, distance=d, qualified=valid, loss=loss))
    total = sum(weight * sum(groups[key]) / (len(groups[key]) + 1e-8) for key, weight in [('full', .2), ('partial', .1)])
    return {'loss': total, 'counts': {k: len(v) for k, v in groups.items()}, 'pairs': pairs}


def angular_update(theta=.2, margin=.8, steps=80):
    trace = []
    for step in range(steps + 1):
        distance = 1 - math.cos(theta)
        trace.append({'step': step, 'angle': theta, 'distance': distance, 'loss': max(0, margin - distance)})
        if distance < margin:
            theta += .1 * math.sin(theta)  # 損失 m - (1-cos(theta)) の勾配と逆向きに角度を動かす。
    return trace


def compute():
    ids = ['a', 'a', 'c', 'b', 'd', 'e']  # 前半は起点、後半は同じ順に並べた正例。
    sids = [(1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 2), (1, 1, 1, 1), (1, 1, 2, 2), (2, 2, 2, 2)]
    angles = [0, 0, .1, .15, .2, 1.5]
    masked = hamr(ids, sids, angles, 3)
    unmasked = hamr(ids, sids, angles, 3, False)
    frames = []
    for degrees in range(0, 181, 10):
        d = 1 - math.cos(math.radians(degrees))
        frames.append({'value': degrees, 'lines': [], 'bars': [
            {'label': '全桁一致の損失', 'value': pair_loss(0, d)},
            {'label': '一部一致の損失', 'value': pair_loss(1, d)},
            {'label': '同じ商品・正例', 'value': pair_loss(0, d, False)}],
            'note': f'角度は{degrees}度、コサイン距離は{d:.4f}。違う桁の数は変えず、符号は割り当て直さない。'})
    trace = angular_update()
    return {'note': '式8–13をもとに、組を除外する条件、群ごとの損失の平均、角度を広げる処理だけを試す。SIDは固定し、量子化器と推薦モデルは学習しない。',
            'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'},
            'checks': {'benign_mask_and_margin': 'CONFIRMED', 'discrete_collision_reduction_in_fixed_SIDs': 'NOT OBSERVED', 'online_GMV': 'NOT TESTED'},
            'experiments': [{'name': '組を除外する場合としない場合の損失、角度を広げる前後の距離', 'n': 6, 'metrics': {'masked_HaMR': masked['loss'], 'unmasked_HaMR': unmasked['loss'], 'initial_distance': trace[0]['distance'], 'final_distance': trace[-1]['distance']}}],
            'masked': masked, 'unmasked': unmasked, 'angular_trace': trace,
            'explorer': {'label': '二つの表現ベクトルの角度', 'unit': '度', 'metric': '重み付け前の組ごとの損失', 'default': 2, 'frames': frames}}


if __name__ == '__main__':
    Path(__file__).with_name('results.json').write_text(json.dumps(compute(), ensure_ascii=False, indent=2) + '\n')
