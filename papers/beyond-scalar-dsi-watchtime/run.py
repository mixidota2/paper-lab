"""Deterministic interface counterexample, not a trained DSI reproduction."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATES = ['early', 'mid', 'completion', 'overplay']


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
    # Same duration and conditional mean: context has no extra distinguishing input.
    cohorts = [[(10, 1.)], [(0, .5), (20, .5)]]
    summaries = [summarize(a) for a in cohorts]
    curves = []
    frames = []
    for step in range(5):
        mixture = step/4
        atoms = [(0, mixture/2), (10, 1-mixture), (20, mixture/2)]
        s = summarize(atoms)
        curves.append({'mixture': mixture, **s})
        bars = ''.join(f'<div><strong>{w}: {s["event_mass"][w]:.0%}</strong><div style="height:22px;background:#e2e8f0;border-radius:4px"><div style="height:100%;width:{s["event_mass"][w]*100}%;background:#167d8d;border-radius:4px"></div></div></div>' for w in STATES)
        frames.append(f'<p>動画10秒・予測平均10秒は固定。0秒と20秒への分岐を {mixture:.0%} 混ぜる。</p>{bars}<p>completion {s["event_mass"]["completion"]:.0%} / overplay {s["event_mass"]["overplay"]:.0%} / long {s["long_probability"]:.0%}</p>')
    # Eq. 5 support on a deliberately small integer-second grid.
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
              'limitations': ['No provider or readout training', 'Hand-designed oracle distributions', 'No public dataset benchmark or production A/B']}
    (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    method = '''## 同じ平均の背後にある四つの状態を残す

著者の提案は、推定器から下流の判断へ渡す情報を増やすことだ。Fig. 2では、状態と時刻の同時分布276値を27次元へ要約し、固定した推定器の出力を複数の読み出し層へ渡す。下流は共通の生特徴も受け取る。

状態は視聴時間 y と動画長 d の比で定義する。early は y/d < 0.3、mid は 0.3 ≤ y/d < 0.9、completion は 0.9 ≤ y/d ≤ 1.1、overplay は y/d > 1.1。overplay は意図的な再視聴を観測したラベルではない。

次の操作は学習済みモデルの予測ではない。同じ動画長と平均を持つ人工分布を切り替え、平均から消える情報を確認する。

'''
    options = ''.join(f'<option value="{i}">{i*25}% 分岐</option>' for i in range(5))
    method += f'<figure class="teaching" data-b21><h3>平均10秒でも、完了確率は変わる</h3><label>分布を混ぜる <select>{options}</select></label><div data-output aria-live="polite">{frames[0]}</div><script type="application/json" data-frames>{json.dumps(frames,ensure_ascii=False)}</script><figcaption>run.py の合成分布。棒は各状態の確率。0秒と20秒の分岐を増やしても平均10秒は変わらない。</figcaption></figure>\n\n'
    method += '解釈: 平均と動画長だけを受け取る層は、この二群を区別できない。状態確率を渡せば完了や長時間視聴を別々に判断できる。ただし、真の分布を正しく推定できるかは別の問題であり、この例では検証しない。\n'
    (ROOT/'method.md').write_text(method)
    print(json.dumps(result['checks'],ensure_ascii=False))


if __name__ == '__main__':
    main()
