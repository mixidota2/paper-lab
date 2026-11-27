"""著者の報告値と、架空の店舗で計算した結果を別々に表示する。
標準ライブラリだけを使う。元の個票は使用せず、外部通信も行わない。
通常実行で結果のJSONと二つのMarkdownを生成し、--testで数値を確かめる。
"""
from pathlib import Path
import json
import math
import sys
import unittest
from itertools import product

ROOT = Path(__file__).resolve().parent
REPORTED = {
    'household': {'label': '主要指標：家庭が週に青果を買う確率の差', 'unit': 'ポイント',
                  'domain': [-10, 10], 'rows': [
                      ['介入前', -0.1, -6.1, 6.0], ['3か月', 0.6, -5.6, 6.7], ['6か月', 3.3, -2.5, 9.2]],
                  'locator': '本文§3.3・表3（改装店側と対照店側の差）'},
    'store': {'label': '副次指標：店舗の青果販売は、改装しなかった場合の予測とどれだけ違うか', 'unit': 'SD',
              'domain': [-0.6, 0.6], 'rows': [
                  ['導入直後', 0.32, 0.11, 0.53], ['3か月', 0.23, -0.05, 0.52], ['6か月', 0.18, -0.16, 0.52]],
              'locator': '本文§3.2・図2〜4（各組の時系列を分析して統合）'},
}


def line_fit(points):
    """最小二乗法で切片と傾きを求める。信頼区間は計算しない。"""
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    slope = sum((x-mx)*(y-my) for x, y in points) / sum((x-mx)**2 for x, _ in points)
    return my-slope*mx, slope


def simulate(control_change=0.0, shock=0.0, mismatch=0.0):
    """架空の2店を導入前12週から導入後26週まで設定する。持続効果は0.20。
    control_changeは両店に共通する傾きの変化、mismatchは改装店だけの傾きの変化。
    shockは再開直後の上振れで、4週で初期値のおよそ37%に減る。
    2店の差に前後別の最小二乗法を適用する。原論文の推定方法とは異なる。
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
    interval_note = (
        "導入直後の区間は要旨を採用した。本文§3.2は上限を0.5と表記している。"
        if key == 'store' and index == 0 else ""
    )
    return f'''<h3>{s['label']}</h3><p><strong>{label}：{value:+g} {s['unit']}</strong>。95% CI [{lo:g}, {hi:g}]（信頼区間）</p>
<svg viewBox="0 0 560 150" role="img" aria-label="{label}、推定値{value}、95%信頼区間{lo}から{hi}、単位{s['unit']}">
<line x1="35" y1="90" x2="525" y2="90" stroke="#627782"/>
<line x1="{x(0)}" y1="25" x2="{x(0)}" y2="100" stroke="#777" stroke-dasharray="4 4"/>
<path d="M{x(lo)},48 V72 M{x(lo)},60 H{x(hi)} M{x(hi)},48 V72" stroke="#006d62" stroke-width="4" fill="none"/>
<circle cx="{x(value)}" cy="60" r="7" fill="#006d62"/>
<text x="35" y="120" font-size="16">{low:g}</text><text x="{x(0)}" y="120" text-anchor="middle" font-size="16">0</text><text x="525" y="120" text-anchor="end" font-size="16">{high:g} {s['unit']}</text></svg>
<p>{'信頼区間は0をまたぐ。この推定では、増えたか減ったかははっきりしない。' if crosses else '店舗販売の信頼区間は0より上にある。導入直後の販売数量についての結果で、買う家庭が継続して増えたかは分からない。'}</p>
<p class="caption">出典：{s['locator']}。点は著者の推定値、線は95%信頼区間。{interval_note}</p>'''


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
    return f'''<p class="key">教材の設定値は、共通の傾き変化 {s['control_change']:+.2f}／週、改装ショック {s['shock']:.1f}、介入店だけの傾き変化 {s['mismatch']:+.2f}／週。改装ショックは再開直後の一時的な上振れを表す。</p>
<svg viewBox="0 0 580 310" role="img" aria-label="教材の2店の販売推移。青は対照店、緑は改装店、橙の破線は改装しなかった場合の推定、紫の点線は改装店に当てはめた線。">
<path d="M45,25 V255 H545" fill="none" stroke="#777"/>{yticks}<line x1="{x(0)}" y1="25" x2="{x(0)}" y2="255" stroke="#999" stroke-dasharray="4 4"/>{paths}{ticks}<text x="290" y="302" text-anchor="middle" font-size="15">改装後の営業再開を0とした週</text></svg>
<p class="caption">青は対照店、緑は改装店の架空の販売推移。橙の破線は配置と品ぞろえを変えなかった場合の推定、紫の点線は改装店のデータに当てはめた線を示す。縦軸はこの教材の単位を使うため、論文のSDとは比較できない。</p>
<table><thead><tr><th>時点</th><th>対照なし</th><th>対照あり</th><th>設定した<br>介入効果</th></tr></thead><tbody>{table}</tbody></table>
<p>「対照なし」の推定は、改装店の導入前の直線を延長して比べる。「対照あり」の推定は、対照店に起きた変化も差し引く。どちらも、同じ架空のデータに当てはめた直線から計算する。</p>'''


def render():
    scenarios = [simulate(c,s,m) for c,s,m in product([-.04,0,.04],[0,.4,.8],[-.02,0,.02])]
    result = {'note':'reportedには著者の報告値、syntheticにはLabが架空の2店で計算した値を入れた。著者の個票は使っていない。',
              'reported':REPORTED, 'synthetic':scenarios,
              'verification':{'mechanism':'PARTIAL','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}}
    (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    ci = {key:[ci_frame(key,i) for i in range(3)] for key in REPORTED}
    evidence = STYLE + '''\n<div class="wrapped-widget" id="wrapped-effects">
<p class="key">原論文の推定値を、指標と時点を選んで読む</p>
<label>指標<select id="wrapped-outcome"><option value="household">主要指標：家庭の購入確率（ポイント）</option><option value="store">副次指標：店舗の販売数量（標準偏差）</option></select></label>
<label>追跡時点<select id="wrapped-time"><option value="0">介入前（家庭）／導入直後（店舗）</option><option value="1">3か月</option><option value="2" selected>6か月</option></select></label>
<output id="wrapped-ci" aria-live="polite">''' + ci['household'][2] + '''</output>
<noscript>JavaScriptが動かない場合、図には家庭の6か月後の値を表示します。全時点の値は下の表と結果JSONで読めます。</noscript></div>
<script>
(()=>{const frames=''' + json.dumps(ci,ensure_ascii=False) + ''';const a=document.getElementById('wrapped-outcome'),b=document.getElementById('wrapped-time');const update=()=>document.getElementById('wrapped-ci').innerHTML=frames[a.value][+b.value];a.addEventListener('change',update);b.addEventListener('change',update);})();
</script>

店舗では、著者は青果を何個売ったかを調べた。全商品の売上金額は対象ではない。家庭では、著者は各週に青果を買ったかを会員カードの記録で調べた。同じ家庭が多く買っても店全体の販売数量は増えるため、二つの指標は別に読む。

| 指標 | 介入前／導入直後 | 3か月 | 6か月 |
|---|---|---|---|
| 主要：家庭の確率差（ポイント） | −0.1 [−6.1, 6.0]（介入前） | +0.6 [−5.6, 6.7] | +3.3 [−2.5, 9.2] |
| 副次：店舗の差（SD） | +0.32 [0.11, 0.53]（導入直後） | +0.23 [−0.05, 0.52] | +0.18 [−0.16, 0.52] |

括弧内は95%信頼区間。家庭の行は各時点の購入確率の群間差であり、Labが導入前の差を引いた値ではない。購買データを提供した475人のうち、227人は改装店側、248人は対照店側だった。6か月後の値は、その時期の週ごとの購入確率である。住民全体が半年間に一度でも買った割合や、健康が改善した割合ではない。店舗の導入直後の区間は要旨の0.11〜0.53を採用した。本文§3.2の上限表記は0.5である。

著者は、電話で聞き取った食事と家庭での廃棄も、副次指標として報告した。6か月後の食事の質のスコアは、改装店側の女性で0.25標準偏差高かった（95%信頼区間0.10〜0.40）。子どもの差は0.06標準偏差で、区間は0を含んだ（−0.13〜0.24）。家庭が生の野菜を捨てたと答えた頻度は、改装店側で週0.20回高かった（0.07〜0.32）。廃棄の重さを測った値ではない（§3.4〜3.5、表4・表5）。

[一次資料：Vogel et al. (2026), §2.4–2.5, §3.2–3.3, Figs 2–5 / Table 3](https://doi.org/10.1371/journal.pmed.1004575)。著者は改装の実施状況を調べた後、入口側へどのくらい移したかで店舗を分けて比べた。本文には >14m と ≥14m の両方の表記があり、14mちょうどの扱いは明確でない。Labはこの事後の比較を主要な結果として扱わない。
'''
    (ROOT/'evidence.md').write_text(evidence)
    frames = [toy_frame(s) for s in scenarios]
    intro = '''### 改装店の販売が伸びたとき、対照店を使うと何が変わるか

Labは、配置と品ぞろえの変更で架空の改装店の販売が毎週0.20高くなるように設定した。ほかの変化をすべて0にすると、対照店を使っても使わなくても推定は+0.20になる。両店に共通する変化を加えた場合は、対照店を使う推定だけが+0.20に戻る。再開直後の上振れや改装店だけの変化を加えると、対照店を使っても推定がずれる。

Labは架空の1組に39週分のデータを作り、改装前後の直線を当てはめた。著者の個票、店舗18組の分析、Fisher–Yates変換、時点間の相関は再現していない。13週と26週は3か月と6か月の目安で、実店舗の実施日ではない。

'''
    widget = STYLE + '''\n<div class="wrapped-widget" id="wrapped-toy">
<label>改装後に両店で共通して変わる販売の伸び<select id="wrapped-control"><option value="0">−0.04／週</option><option value="1" selected>0／週</option><option value="2">+0.04／週</option></select></label>
<label>改装店で営業を再開した直後の上振れ<select id="wrapped-shock"><option value="0">なし</option><option value="1">+0.4（4週で約37%に減衰）</option><option value="2">+0.8（4週で約37%に減衰）</option></select></label>
<label>対照店にはない、改装店だけの販売の伸びの変化<select id="wrapped-mismatch"><option value="0">−0.02／週</option><option value="1" selected>0／週</option><option value="2">+0.02／週</option></select></label>
<button id="wrapped-reset" type="button">初期条件へ戻す</button>
<output id="wrapped-simulation" aria-live="polite">''' + frames[10] + '''</output>
<noscript>JavaScriptが動かない場合は初期条件を表示します。計算をやり直す手順は下にあります。</noscript></div>
<script>
(()=>{const frames=''' + json.dumps(frames,ensure_ascii=False) + ''';const controls=['control','shock','mismatch'].map(x=>document.getElementById('wrapped-'+x));const update=()=>{const [c,s,m]=controls.map(x=>+x.value);document.getElementById('wrapped-simulation').innerHTML=frames[c*9+s*3+m];};controls.forEach(x=>x.addEventListener('change',update));document.getElementById('wrapped-reset').addEventListener('click',()=>{controls.forEach((x,i)=>x.value=[1,0,1][i]);update();});})();
</script>

### 教材は何を設定し、何を推定するか

tは営業再開から数えた週で、Pは再開前に0、再開後に1を取る。Labは対照店の値を Cₜ = 1 + 0.01t + c·tP、改装店の値を Iₜ = 1.4 + 0.03t + (c+u)tP + 0.20P + s·exp(−t/4)P と設定した。cは両店に共通する傾きの変化、uは改装店だけの傾きの変化、sは再開直後の上振れである。

Labは2店の差 Dₜ = Iₜ − Cₜ に、Dₜ = a + bt + δP + γtP を最小二乗法で当てはめる。再開からh週がたったときの推定差は δ + γh である。推定式には、再開直後の上振れが徐々に小さくなる項を入れていない。そのため、上振れを再開後の水準や傾きの変化の一部として数える。改装店だけの傾きの変化uも、位置と品ぞろえの効果とは区別できない。この式は教材のもので、原論文の補足資料S2 Boxの式ではない。

Labは乱数を使わず、Pythonで27条件の値を計算する。信頼区間は計算しない。ページの操作は保存した図と表を切り替える。+0.20はこの教材の設定値であって、実店舗の効果ではない。
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
        print('著者の報告値と、架空の店舗での計算値を分けて保存しました。')
