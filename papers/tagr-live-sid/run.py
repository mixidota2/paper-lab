"""固定した語彙で広告のIDを付け直す人工例。学習済みのLSIDや本番データは使わない。"""
from collections import Counter
import json
from pathlib import Path

CENTERS = (0., 1., 2., 3.)


def encode(xs):
    return [min(range(len(CENTERS)), key=lambda k: abs(x-CENTERS[k])) for x in xs]


def metrics(ids, original, current):
    counts = Counter(ids)
    return {'cpr': len(ids)/len(counts),
            'col': sum(n>1 for n in counts.values())/len(counts),
            'assignment_stability': sum(a==b for a,b in zip(ids,original))/len(ids),
            'semantic_mse': sum((CENTERS[k]-x)**2 for k,x in zip(ids,current))/len(ids)}


def scenario(current):
    old = encode([.05, .10, 1.05, 1.10])
    return {'features_after': current, 'static_ids': old, 'refreshed_ids': encode(current),
            'static': metrics(old, old, current), 'refreshed': metrics(encode(current), old, current)}


def schedule(period):
    # 同じ数値を、教師あり学習では0へ、追加更新では交互に+1と−1へ近づける。
    # 追加更新の回数も出力する。更新回数をそろえたGRPOの比較ではない。
    x = 0.
    rows = []
    updates = 0
    for step in range(80):
        x -= .2*x
        if step >= 20 and (step-20) % period == 0:
            reward_target = 1 if updates%2 == 0 else -1
            x += .6*(reward_target-x)
            updates += 1
        rows.append(x*x)
    return {'reward_updates': updates, 'mean_supervised_loss_after_warmup': sum(rows[20:])/60,
            'peak_supervised_loss': max(rows), 'loss_trace': rows}


def experiment():
    return {'kind': '固定した語彙への割り当てと、追加更新の頻度を比べる人工例', 'seed': 'deterministic',
            'spread': scenario([.05, 1.05, 2.05, 3.05]),
            'collapse_counterexample': scenario([.05, .05, .05, .05]),
            'schedules': {'continuous': schedule(1), 'intermittent': schedule(5)},
            'not_tested': ['RQ-KMeans', 'collaborative alignment', 'GRPO reward', 'production latency', 'revenue']}

if __name__ == '__main__':
    result = experiment()
    Path(__file__).with_name('results.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
