"""平均と動画長だけでは視聴の状態を区別できないことを、合成例で確かめる。"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATES = ['early', 'mid', 'completion', 'overplay']
DISPLAY = {'early': '短時間の視聴', 'mid': '途中までの視聴',
           'completion': '終了付近の視聴', 'overplay': '動画長の110%を超える視聴'}


def state(y, d):
    ratio = y / d
    return 'early' if ratio < .3 else 'mid' if ratio < .9 else 'completion' if ratio <= 1.1 else 'overplay'


def summarize(atoms, d=10):
    mass = {w: sum(p for y, p in atoms if state(y, d) == w) for w in STATES}
    return {'mean_seconds': sum(y*p for y, p in atoms), 'duration': d,
            'event_mass': mass, 'long_probability': mass['completion']+mass['overplay'],
            'entropy': -sum(p*math.log(p) for p in mass.values() if p)}


def expected_brier(atoms, probability, target):
    return sum(p*(probability-int(state(y, 10) == target))**2 for y, p in atoms)


def main():
    # どちらも10秒の動画で、平均視聴時間は10秒。追加の入力では二群を区別しない。
    cohorts = [[(10, 1.)], [(0, .5), (20, .5)]]
    summaries = [summarize(a) for a in cohorts]
    curves = []
    frames = []
    for step in range(5):
        mixture = step/4
        atoms = [(0, mixture/2), (10, 1-mixture), (20, mixture/2)]
        s = summarize(atoms)
        curves.append({'mixture': mixture, **s})
        bars = ''.join(f'<div><strong>{DISPLAY[w]}：{s["event_mass"][w]:.0%}</strong><div style="height:22px;background:#e2e8f0;border-radius:4px"><div style="height:100%;width:{s["event_mass"][w]*100}%;background:#167d8d;border-radius:4px"></div></div></div>' for w in STATES)
        frames.append(f'<p>動画の長さも平均視聴時間も10秒です。0秒か20秒を見る群を全体の{mixture:.0%}にしました。</p>{bars}<p>終了付近 {s["event_mass"]["completion"]:.0%} ／ 110%超 {s["event_mass"]["overplay"]:.0%} ／ 両方を合わせた割合 {s["long_probability"]:.0%}</p>')
    # 式5の範囲を、0〜20秒を1秒刻みにした格子で確かめる。
    support = {w: [t for t in range(21) if (t == 10 if w == 'completion' else state(t, 10) == w)] for w in STATES}
    allowed = sum(len(v) for v in support.values())
    masked_mass = {w: {str(t): (1/allowed if t in support[w] else 0.) for t in range(21)} for w in STATES}
    checks = {
        'same_mean_and_duration': summaries[0]['mean_seconds'] == summaries[1]['mean_seconds'] == 10,
        'different_overplay_mass': summaries[0]['event_mass']['overplay'] == 0 and summaries[1]['event_mass']['overplay'] == .5,
        'support_normalized': abs(sum(sum(v.values()) for v in masked_mass.values())-1) < 1e-12,
        'completion_anchor': support['completion'] == [10],
        'boundary_labels': [state(y, 10) for y in [2.9,3,8.9,9,11,11.1]] == ['early','mid','mid','completion','completion','overplay'],
    }
    assert all(checks.values())
    result = {'experiment': 'oracle-distribution-interface-counterexample', 'seed': None,
              'verification': {'mechanism': 'PARTIAL', 'performance': 'NOT TESTED', 'scaling': 'NOT TESTED', 'production_applicability': 'NOT TESTED'},
              'cohorts': summaries, 'mixture_sweep': curves, 'support': support,
              'expected_overplay_brier': {'best_shared_scalar_readout': sum(expected_brier(a,.25,'overplay') for a in cohorts)/2, 'oracle_distribution_readout': sum(expected_brier(a,s['event_mass']['overplay'],'overplay') for a,s in zip(cohorts,summaries))/2},
              'checks': {k: 'CONFIRMED' if v else 'NOT OBSERVED' for k,v in checks.items()},
              'limitations': ['分布を推定するモデルや後段のモデルは学習していない', '分布はLabが先に決めた', '公開データでの精度比較や本番のA/Bテストは実施していない']}
    (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    method = '''## 視聴時間の平均からは、終了付近まで見た割合が分からない

DSIは、どのくらいの時間まで視聴が続くかを推薦に使います。著者は、視聴の状態と時間の区間を組み合わせた276個の確率を、状態ごとの確率や平均秒数を含む27個の値にまとめます（図2）。分布を推定するモデルを学習した後は、その重みを固定します。視聴秒数を予測するモデルと順位を付けるモデルは、27個の値に利用者や動画などの元の特徴を加えて学習します。

視聴時間を動画の長さで割ると、同じ10秒でも動画のどこまで見たかを比べられます。著者はその比率を使い、30%未満を短時間、30%以上90%未満を途中、90%以上110%以下を終了付近、110%を超える場合をoverplayと呼びます。終了付近には、最後まで再生しなかった視聴も含まれます。110%を超えても、利用者が意図して見直したかは分かりません。

### 動画の長さと平均をそろえて、見方の違いを調べる

Labは10秒の動画に対して2種類の見方を設定しました。片方の群では全員が10秒見ます。もう片方では、半数が0秒、残りの半数が20秒見ます。どちらの群でも平均は10秒です。下の選択欄で、後者の群を全体の何割にするか変えられます。表示するのは、先に決めた視聴時間から計算した確率であり、モデルの予測ではありません。

'''
    options = ''.join(f'<option value="{i}">{i*25}%</option>' for i in range(5))
    method += f'<figure class="teaching" data-b21><h3>平均10秒のまま、視聴の内訳が変わる</h3><label>0秒か20秒を見る群の割合 <select>{options}</select></label><div data-output aria-live="polite">{frames[0]}</div><script type="application/json" data-frames>{json.dumps(frames,ensure_ascii=False)}</script><figcaption>棒は4つの状態が占める割合です。0秒と20秒の人数を同じにすると、二つの群をどの割合で混ぜても平均は10秒です。</figcaption></figure>\n\n'
    method += '動画の長さと平均視聴時間だけを受け取るモデルには、二群を見分ける情報がありません。状態ごとの確率が分かれば、終了付近まで見る割合と110%を超えて見る割合を別に扱えます。論文のlongはこの二つを合計した値です。実際の視聴データからこの確率をどれだけ正確に求められるかは、Labでは検証していません。\n'
    (ROOT/'method.md').write_text(method)
    print(json.dumps(result['checks'],ensure_ascii=False))


if __name__ == '__main__':
    main()
