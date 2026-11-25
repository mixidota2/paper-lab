"""Deterministic teaching experiment, not a replication of WRAPPED.
Standard library only. uv run run.py [--test]. Generates results.json and two
interactive Markdown sections. No source data or external requests are used.
"""
from pathlib import Path
import json
import math
import sys
import unittest
from itertools import product

ROOT = Path(__file__).resolve().parent
REPORTED = {
    'household': {'label': '主要：家庭の週ごとの青果購入確率の群間差', 'unit': 'ポイント',
                  'domain': [-10, 10], 'rows': [
                      ['介入前', -0.1, -6.1, 6.0], ['3か月', 0.6, -5.6, 6.7], ['6か月', 3.3, -2.5, 9.2]],
                  'locator': '本文 §3.3・Table 3（群間のモデル推定確率差）'},
    'store': {'label': '副次：店舗の青果販売個数と反実仮想との差', 'unit': 'SD',
              'domain': [-0.6, 0.6], 'rows': [
                  ['導入直後', 0.32, 0.11, 0.53], ['3か月', 0.23, -0.05, 0.52], ['6か月', 0.18, -0.16, 0.52]],
              'locator': '本文 §3.2・Figs 2–4（対応店舗別ITSの統合）'},
}


def line_fit(points):
    """Ordinary least squares with intercept; no uncertainty estimate."""
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    slope = sum((x-mx)*(y-my) for x, y in points) / sum((x-mx)**2 for x, _ in points)
    return my-slope*mx, slope


def simulate(control_change=0.0, shock=0.0, mismatch=0.0):
    """One fictional matched pair, weeks -12..26, permanent effect 0.20.
    control_change is a COMMON post-intervention slope change. mismatch is an
    untreated intervention-only slope change that violates the counterfactual.
    shock is intervention-only refurbishment, decaying with time constant 4w.
    Pre and post OLS of I-C is equivalent to a fully interacted segmented
    regression on the pair difference; this is NOT the paper's GLS estimator.
    """
    rows = []
    for t in range(-12, 27):
        post = int(t >= 0)
        c = 1 + .01*t + post*control_change*t
        untreated = 1.4 + .03*t + post*(control_change+mismatch)*t
        i = untreated + post*(.20 + shock*math.exp(-t/4))
        rows.append({'week': t, 'control': c, 'intervention': i,
                     'true_untreated': untreated, 'difference': i-c})
    before = [r for r in rows if r['week'] < 0]
    after = [r for r in rows if r['week'] >= 0]
    pre = line_fit([(r['week'], r['difference']) for r in before])
    post = line_fit([(r['week'], r['difference']) for r in after])
    pre_i = line_fit([(r['week'], r['intervention']) for r in before])
    post_i = line_fit([(r['week'], r['intervention']) for r in after])
    for r in rows:
        t = r['week']
        r['counterfactual'] = r['control'] + pre[0]+pre[1]*t
        r['fitted'] = r['control'] + (pre[0]+pre[1]*t if t < 0 else post[0]+post[1]*t)
    effects = [{'week': h, 'controlled': post[0]-pre[0]+(post[1]-pre[1])*h,
                'without_control': post_i[0]-pre_i[0]+(post_i[1]-pre_i[1])*h,
                'true_placement_and_range': .20} for h in [0, 13, 26]]
    return {'control_change': control_change, 'shock': shock, 'mismatch': mismatch,
            'rows': rows, 'effects': effects}


STYLE = '''<style>
.wrapped-widget{border:1px solid #9eaeb8;border-radius:16px;padding:clamp(12px,3vw,24px);margin:1.5rem 0;background:#f7faf9;color:#182c35;max-width:100%;overflow:hidden}
.wrapped-widget label{display:block;margin:12px 0;font-weight:650}.wrapped-widget select{display:block;width:100%;max-width:100%;padding:10px;background:white;color:#182c35;border:1px solid #697e8a;border-radius:6px;font:inherit}
.wrapped-widget svg{display:block;width:100%;height:auto}.wrapped-widget table{width:100%;font-size:.9rem}.wrapped-widget th,.wrapped-widget td{padding:5px!important}.wrapped-widget .caption{font-size:.9rem}.wrapped-widget output{display:block}.wrapped-widget .key{font-weight:700;color:#005c50}
</style>'''


def ci_frame(key, index):
    s = REPORTED[key]
    label, value, lo, hi = s['rows'][index]
    low, high = s['domain']
    def x(v): return 35 + (v-low)/(high-low)*490
    crosses = lo <= 0 <= hi
    return f'''<h3>{s['label']}</h3><p><strong>{label}：{value:+g} {s['unit']}</strong> ／95% CI [{lo:g}, {hi:g}]</p>
<svg viewBox="0 0 560 150" role="img" aria-label="{label}、推定値{value}、95%信頼区間{lo}から{hi}、単位{s['unit']}">
<line x1="35" y1="90" x2="525" y2="90" stroke="#627782"/>
<line x1="{x(0)}" y1="25" x2="{x(0)}" y2="100" stroke="#777" stroke-dasharray="4 4"/>
<path d="M{x(lo)},48 V72 M{x(lo)},60 H{x(hi)} M{x(hi)},48 V72" stroke="#006d62" stroke-width="4" fill="none"/>
<circle cx="{x(value)}" cy="60" r="7" fill="#006d62"/>
<text x="35" y="120" font-size="16">{low:g}</text><text x="{x(0)}" y="120" text-anchor="middle" font-size="16">0</text><text x="525" y="120" text-anchor="end" font-size="16">{high:g} {s['unit']}</text></svg>
<p>{'信頼区間は0をまたぐため、この比較では増えたか減ったかを決められません。効果がなかったと証明したわけでもありません。' if crosses else '信頼区間は0より上です。導入直後の店舗販売の結果であり、家庭が継続して買うようになったことを示す値ではありません。'}</p>
<p class="caption">出典：{s['locator']}。点は著者の推定値、線は95%信頼区間です。Labの小実験の値ではありません。</p>'''


def toy_frame(s):
    rows = s['rows']
    # Fixed axes across ALL conditions; units deliberately not paper SD units.
    def x(t): return 45+(t+12)/38*500
    def y(v): return 250-(v+0.5)/4*210
    paths = ''
    for key, color, dash in [('control','#526f9d',''),('intervention','#007868',''),('counterfactual','#a64c19','6 4'),('fitted','#663c86','2 3')]:
        points = ' '.join(f'{x(r["week"]):.2f},{y(r[key]):.2f}' for r in rows)
        paths += f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dash}"/>'
    ticks = ''.join(f'<text x="{x(t):.2f}" y="278" text-anchor="middle" font-size="15">{t}</text>' for t in [-12,0,13,26])
    yticks = ''.join(f'<text x="36" y="{y(v)+5:.2f}" text-anchor="end" font-size="14">{v:g}</text>' for v in [0,1,2,3])
    table = ''.join(f'<tr><th>{e["week"]}週</th><td>{e["without_control"]:+.3f}</td><td>{e["controlled"]:+.3f}</td><td>+0.200</td></tr>' for e in s['effects'])
    return f'''<p class="key">合成データのみ：共通の傾き変化 {s['control_change']:+.2f}／週、改装ショック {s['shock']:.1f}、介入店だけの傾き変化 {s['mismatch']:+.2f}／週</p>
<svg viewBox="0 0 580 310" role="img" aria-label="人工の対応店舗の時系列。青は対照、緑は介入、橙の破線は対照から組み立てた反実仮想、紫の点線は介入店の当てはめ">
<path d="M45,25 V255 H545" fill="none" stroke="#777"/>{yticks}<line x1="{x(0)}" y1="25" x2="{x(0)}" y2="255" stroke="#999" stroke-dasharray="4 4"/>{paths}{ticks}<text x="290" y="302" text-anchor="middle" font-size="15">導入からの週（0＝再開）</text></svg>
<p class="caption">青は対照店、緑は介入店です。橙の破線は、配置と品ぞろえを変えなかった場合の推定です。紫の点線は介入店の人工データに当てはめた線です。縦軸には、論文のSDとは比較できない、この小実験だけの単位を使います。</p>
<table><thead><tr><th>時点</th><th>対照なし</th><th>対照あり</th><th>設定した<br>介入効果</th></tr></thead><tbody>{table}</tbody></table>
<p>「対照なし」は介入店の導入前の直線だけを延長する。「対照あり」は対照店で起きた変化も差し引く。両者とも同じ人工系列に当てはめた直線の差である。</p>'''


def render():
    scenarios = [simulate(c,s,m) for c,s,m in product([-.04,0,.04],[0,.4,.8],[-.02,0,.02])]
    result = {'note':'reportedは原論文の転記、syntheticは自作の決定的実験。個票の再現ではない。',
              'reported':REPORTED, 'synthetic':scenarios,
              'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}}
    (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    ci = {key:[ci_frame(key,i) for i in range(3)] for key in REPORTED}
    evidence = STYLE + '''\n<div class="wrapped-widget" id="wrapped-effects">
<p class="key">原論文の報告値 · 単位と追跡時点を確かめる</p>
<label>指標<select id="wrapped-outcome"><option value="household">主要：家庭の購入確率（ポイント）</option><option value="store">副次：店舗の青果販売個数（SD）</option></select></label>
<label>追跡時点<select id="wrapped-time"><option value="0">介入前（家庭）／導入直後（店舗）</option><option value="1">3か月</option><option value="2" selected>6か月</option></select></label>
<output id="wrapped-ci" aria-live="polite">''' + ci['household'][2] + '''</output>
<noscript>切替にはJavaScriptが必要です。初期表示は家庭の6か月値です。全数値は本文表と結果JSONでも読めます。</noscript></div>
<script>
(()=>{const frames=''' + json.dumps(ci,ensure_ascii=False) + ''';const a=document.getElementById('wrapped-outcome'),b=document.getElementById('wrapped-time');const update=()=>document.getElementById('wrapped-ci').innerHTML=frames[a.value][+b.value];a.addEventListener('change',update);b.addEventListener('change',update);})();
</script>

店舗の指標は、店全体で青果を何個売ったかです。全商品の売上金額ではありません。家庭の指標は、会員カードでその週に青果を買ったかどうかです。同じ家が多く買うだけでも店全体の個数は増えるので、二つの指標は代用できません。

| 指標 | 介入前／導入直後 | 3か月 | 6か月 |
|---|---|---|---|
| 主要：家庭の確率差（ポイント） | −0.1 [−6.1, 6.0]（介入前） | +0.6 [−5.6, 6.7] | +3.3 [−2.5, 9.2] |
| 副次：店舗の差（SD） | +0.32 [0.11, 0.53]（導入直後） | +0.23 [−0.05, 0.52] | +0.18 [−0.16, 0.52] |

表の括弧内はすべて95%信頼区間です。家庭の行は、各時点で著者が推定した介入店側と対照店側の購入確率の差です。Labはこの表から介入前の差を引き直していません。購買データを提供した人は475人（介入227・対照248）でした。6か月時点の週次指標は、すべての住民が半年のうちに一度でも買った割合でも、健康が改善した割合でもありません。

[一次資料：Vogel et al. (2026), §2.4–2.5, §3.2–3.3, Figs 2–5 / Table 3](https://doi.org/10.1371/journal.pmed.1004575)。売場を入口側に14mより遠く動かした店とそれ以外の比較は、著者が実施状況を調べたあとに追加しました。14mちょうどをどちらの組に入れるかは本文内で >14m と ≥14m の両方の表記があり、Labはこの区分の結果を主な効果として使っていません。
'''
    (ROOT/'evidence.md').write_text(evidence)
    frames = [toy_frame(s) for s in scenarios]
    intro = '''### 同じ上昇でも、対照店と改装の影響で読み方が変わる

Labは、配置と品ぞろえを変えると、架空の店の販売が毎週+0.20増えるように設定しました。ほかの条件をすべて0にすると、対照店を使う方法と使わない方法で推定が一致します。次に両店に共通する変化だけを動かし、どちらが+0.20に戻るかを比べてください。最後に、改装直後だけの上振れや介入店だけの傾きの変化を加えると、対照店があっても推定がずれます。

Labは架空の店舗1組を39週分作り、対照店を使った中断時系列で前後を比べました。論文の個票、18組の推定、Fisher–Yates変換、各時点の相関は再現していません。13・26週は3・6か月の目安であり、論文に登場する店の実施日ではありません。

'''
    widget = STYLE + '''\n<div class="wrapped-widget" id="wrapped-toy">
<label>両店舗に共通する導入後の傾き変化<select id="wrapped-control"><option value="0">−0.04／週</option><option value="1" selected>0／週</option><option value="2">+0.04／週</option></select></label>
<label>介入店だけの一時的な改装ショック<select id="wrapped-shock"><option value="0">なし</option><option value="1">+0.4（4週で約37%に減衰）</option><option value="2">+0.8（4週で約37%に減衰）</option></select></label>
<label>介入店だけの未調整な導入後の傾き変化<select id="wrapped-mismatch"><option value="0">−0.02／週</option><option value="1" selected>0／週</option><option value="2">+0.02／週</option></select></label>
<button id="wrapped-reset" type="button">初期条件へ戻す</button>
<output id="wrapped-simulation" aria-live="polite">''' + frames[10] + '''</output>
<noscript>切替にはJavaScriptが必要です。初期条件と再実行用コードはそのまま読めます。</noscript></div>
<script>
(()=>{const frames=''' + json.dumps(frames,ensure_ascii=False) + ''';const controls=['control','shock','mismatch'].map(x=>document.getElementById('wrapped-'+x));const update=()=>{const [c,s,m]=controls.map(x=>+x.value);document.getElementById('wrapped-simulation').innerHTML=frames[c*9+s*3+m];};controls.forEach(x=>x.addEventListener('change',update));document.getElementById('wrapped-reset').addEventListener('click',()=>{controls.forEach((x,i)=>x.value=[1,0,1][i]);update();});})();
</script>

### この小実験だけの式

tは導入から何週目かを表し、Pは導入後なら1です。対照店は Cₜ = 1 + 0.01t + c·tP。介入店は Iₜ = 1.4 + 0.03t + (c+u)tP + 0.20P + s·exp(−t/4)P です。cは両店に共通する変化、uは介入店だけの傾きの変化、sは改装直後の一時的な上振れを表します。

Labは、2店の差 Dₜ = Iₜ − Cₜ に、Dₜ = a + bt + δP + γtP を最小二乗で当てはめます。h週の推定差は δ + γh です。この式では、改装直後の上振れが時間とともに小さくなる様子を別項にしていません。そのため、上振れの影響を介入後の水準や傾きの変化として拾います。uも配置と品ぞろえの効果と区別できません。これはLabの説明用の式であり、原論文のS2 Boxの式ではありません。

Labは乱数や信頼区間を使わず、27条件をPythonで計算します。ブラウザーは保存した図と表を切り替えます。+0.20はLabがこの例に設定した効果であり、実店舗で同じ値が得られるという意味ではありません。
'''
    (ROOT/'experiment.md').write_text(intro+widget)


class Checks(unittest.TestCase):
    def test_recovery_and_common_trend(self):
        for c in [-.04,0,.04]:
            for e in simulate(c,0,0)['effects']:
                self.assertAlmostEqual(e['controlled'],.20)
                self.assertAlmostEqual(e['without_control'],.20+c*e['week'])
    def test_confounding_not_removed(self):
        e = simulate(0,0,.02)['effects'][2]
        self.assertAlmostEqual(e['controlled'],.72)
    def test_temporary_shock_not_permanent(self):
        e = simulate(0,.8,0)['effects']
        self.assertGreater(e[0]['controlled'],.2)
        self.assertLess(e[-1]['controlled'],.2)
    def test_reported_intervals(self):
        self.assertEqual(REPORTED['household']['rows'][2],['6か月',3.3,-2.5,9.2])
        self.assertEqual(REPORTED['store']['rows'][0],['導入直後',.32,.11,.53])
        for s in REPORTED.values():
            for _, v, lo, hi in s['rows']:
                self.assertLess(lo,v); self.assertLess(v,hi)


if __name__ == '__main__':
    if '--test' in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        render()
        print('Generated results.json, evidence.md, experiment.md (synthetic only).')
