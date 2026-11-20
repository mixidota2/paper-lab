"""October 2 paper-specific views, generated exclusively from results.json."""
import json
from html import escape
from paper_lab.batch28 import table


def svg(body, label, height=360):
    return (f'<svg viewBox="0 0 520 {height}" role="img" aria-label="{escape(label)}" '
            f'style="width:100%;height:auto;max-width:680px">{body}</svg>')


def select_figure(title, label, options, frames, caption):
    choices = ''.join(f'<option value="{i}">{escape(o)}</option>' for i, o in enumerate(options))
    payload = json.dumps(frames, ensure_ascii=False).replace('</', '<\\/')
    return (f'<figure class="teaching" data-b21><h3>{title}</h3>'
            f'<label>{label} <select>{choices}</select></label>'
            f'<script type="application/json" data-frames>{payload}</script>'
            f'<div data-output aria-live="polite">{frames[0]}</div>'
            f'<figcaption>{caption}</figcaption></figure>')


def bars(title, rows, maximum, unit, caption):
    # DOM bars keep labels readable on phones; every bar starts at zero.
    body = ''.join(f'<div class="bar-row"><div class="bar-label"><span>{escape(label)}</span>'
                   f'<strong>{value:.3f}{unit}</strong></div><div class="bar-track" aria-hidden="true">'
                   f'<div class="bar-fill" style="width:{100*value/maximum:.3f}%;background:{color}"></div>'
                   '</div></div>' for label, value, color in rows)
    return f'<figure class="teaching"><h3>{title}</h3><p>共通尺度 0–{maximum}{unit}。小さいほどよい。</p><div class="bar-chart">{body}</div><figcaption>{caption}</figcaption></figure>'


def orpr(r):
    frames = []
    options = []
    max_stock = max(c['stock'] for c in r['candidates'])
    max_loss = max(c['loss'] for c in r['candidates'])
    for case in r['cases']:
        x = lambda loss: 65 + 400*loss/max_loss
        y = lambda stock: 290 - 240*stock/max_stock
        body = '<path d="M65 40V290H480" fill="none" stroke="currentColor"/>'
        body += f'<path d="M{x(case["budget"]):.2f} 40V290" stroke="#aa482e" stroke-dasharray="6 3"/>'
        for c in r['candidates']:
            color = '#137d79' if c['loss'] <= case['budget']+1e-9 else '#abb3b6'
            body += f'<circle cx="{x(c["loss"]):.2f}" cy="{y(c["stock"]):.2f}" r="4" fill="{color}"><title>{c["days"]}日分、期末在庫の合計 {c["stock"]:.2f}、売り逃し{c["loss"]:.2f}</title></circle>'
        best = case['best']
        if best:
            body += f'<circle cx="{x(best["loss"]):.2f}" cy="{y(best["stock"]):.2f}" r="9" fill="none" stroke="#102d47" stroke-width="3"/>'
            text = f'選択：カテゴリA {best["days"][0]}日分、B {best["days"][1]}日分。日ごとの期末在庫の合計 {best["stock"]:.2f}、売り逃し {best["loss"]:.2f}。'
        else:
            text = '条件を満たす候補なし。初日に入荷しないため、どの候補でも売り逃しが上限を超えます。'
        body += f'<text x="65" y="25">期末在庫の合計（単価1）</text><text x="275" y="335">売り逃し（単価1）</text><text x="48" y="312">0</text><text x="440" y="312">{max_loss:.0f}</text><text x="12" y="52">{max_stock:.0f}</text>'
        frames.append(svg(body, text)+f'<p><strong>{text}</strong></p><p>売り逃しの上限 {case["budget"]:.2f}。100候補中 {case["feasible"]}件（緑）が上限以内です。灰色は上限を超えた候補、輪は上限以内で期末在庫の合計が最も少ない候補です。</p>')
        options.append(f'αloss={case["alpha"]:.2f}')
    out = select_figure('売り逃しの上限を変え、補充日数を選ぶ', '売り逃しをどこまで抑えるか（式(2)のαloss）', options, frames,
                        '縦線は売り逃しの上限です。上限は固定した合成需要の合計×(1−αloss)なので、αlossを大きくすると上限が下がります。縦軸は日ごとの期末在庫を足した量、横軸は満たせなかった需要の合計です。どちらも単価1で換算します。原論文§3.3の考え方を使う人工例で、JDの再現ではありません。')
    frames = []
    labels = [('在庫回転日数（TT）', '日', 6), ('欠品しなかった日の割合', '単位と比較基準は表を参照', 3), ('保有費用', '単位と比較基準は表を参照', 32)]
    for j, (label, unit, limit) in enumerate(labels):
        vals = [r['paper_evidence']['field'][key][j] for key in ['psm', 'did']]
        body = ''
        if j == 0:
            # Both estimates are differences in days; only this indicator uses bars.
            for i, (v, name) in enumerate(zip(vals, ['PSM A/B', 'DiD'])):
                y0 = 15 + i*105
                end = 260 + 185*v/limit
                body += f'<path d="M260 {y0}V{y0+65}" stroke="currentColor"/><text x="15" y="{y0+18}">{name}（日）</text><rect x="{min(end,260):.2f}" y="{y0+32}" width="{abs(end-260):.2f}" height="20" fill="#137d79"/><text x="340" y="{y0+18}">{v:+.2f}日</text><text x="250" y="{y0+80}">0</text>'
            chart = svg(body, f'{label}: PSM {vals[0]}, DiD {vals[1]}', 230)
        else:
            references = ['需要や回転日数が近い対象の比較（表3の表記を維持）', '介入前後の変化の差（表4）'] if j == 1 else ['対応付け比較で対照群に比べた変化率', '前年比の差：処置+3.70% − 対照+22.05%']
            chart = table(['比較方法', '報告値', '単位', '比較基準'], [
                ['PSM A/B', f'{vals[0]:+.2f}', '%', references[0]],
                ['DiD', f'{vals[1]:+.2f}', 'ポイント', references[1]],
            ]).replace('aria-label="人工実験の比較"', 'aria-label="著者報告の比較"')
        note = ['どちらも日数の差です。対象を対応付けるPSMと、介入前後の差を比べるDiDは、同じ現場評価の異なる比較であり、独立した2回の実験ではありません。',
                'PSMの+2.29%は原表の表記です。DiDの+0.47ポイントは率の差です。単位と比較基準が違うため、棒の長さでは比べません。',
                'PSMは対照群に比べて29.95%低い値です。DiDでは前年比が対照群+22.05%、適用群+3.70%で、その差は−18.35ポイントです。適用群で保有費用が前年比で減ったわけではありません。'][j]
        frames.append(chart+f'<p><strong>{label}（{unit}）</strong>。{note}</p>')
    return out + select_figure('著者が報告した現場結果を、指標ごとに読む', '表示指標', [x[0] for x in labels], frames,
        '原論文の表3・4から。担当者が選んだ菓子3カテゴリを約30日間評価し、対象を対応付けた比較などを行いました。欠品費用は含みません。')


def proximal(r):
    names = {'counterexample': '図3：PCSPを満たさない強凸関数', 'state': '縮約：区分線形費用＋配置後の在庫状態に加える項', 'action': '縮約：区分線形費用＋行動正則化'}
    options, frames = [], []
    for c in r['cases']:
        xy = lambda p: (70+p[0]*170, 365-p[1]*150)
        points = ' '.join(f'{xy(p)[0]:.4f},{xy(p)[1]:.4f}' for p in c['states'])
        one = next(k['final'] for k in r['cases'] if k['kind']==c['kind'] and k['count']==1)
        ox, oy = xy(one)
        fx, fy = xy(c['final'])
        body = '<path d="M70 45V365H440" stroke="currentColor" fill="none"/><path d="M70 65L410 365" stroke="#ccd7df" stroke-dasharray="5 4"/>'
        body += f'<polyline points="{points}" stroke="#137d79" stroke-width="4" fill="none"/><circle cx="{ox}" cy="{oy}" r="10" fill="none" stroke="#bd5034" stroke-width="3"/><circle cx="{fx}" cy="{fy}" r="5" fill="#137d79"/>'
        body += '<text x="10" y="25">拠点2の在庫 x₂</text><text x="265" y="405">拠点1の在庫 x₁</text><text x="52" y="389">0</text><text x="402" y="389">2</text><text x="43" y="70">2</text>'
        final = ', '.join(f'{v:.4f}' for v in c['final'])
        frames.append(svg(body, f'{names[c["kind"]]}、{c["count"]}回、最終在庫{final}', 425)+f'<p><strong>最終在庫 ({final})、TV={c["tv"]:.6f}</strong></p><p>緑線：順次配置。赤い輪：同じ目的の一括配置。TVは一括配置と順次配置の最終在庫の差。TV = 最終在庫のL1差 / (2×入荷量)。需要・費用変化なし。</p>')
        options.append(f'{names[c["kind"]]} / K={c["count"]}')
    out = select_figure('図3の反例を動かす：先に置いた在庫は戻せない', '目的と分割回数', options, frames,
                         '図3・付録C.1の反例は原式どおり。状態potentialと行動正則化はLab独自の分離可能な比較例。')
    rows = [(name, values[0], '#137d79' if name=='State-prox' else '#72818f') for name, values in r['paper_evidence']['oos'].items()]
    return out + bars('未知商品・別期間：State-proxは0.950、neural RLは1.012', rows, 1.2, '',
        '著者の表1。SCPUTは充足数量当たりの配送・移送費用で、容量価格ペナルティを含まない。その基準値に対する比の平均。標準偏差は根拠の表を参照。オフラインのみ。図4のK=500感度は別条件で、TV 0.00201対0.12716。')


def radfl(r):
    frames, options = [], []
    for case in r['cases']:
        vals = case['candidates']
        lo, hi = min(c['objective'] for c in vals), max(c['objective'] for c in vals)
        body = '<text x="12" y="20">チャネルBへの配分</text><path d="M70 42V350H410" stroke="currentColor" fill="none"/>'
        for c in vals:
            a, b = c['q']; light = 35 + 55*(c['objective']-lo)/(hi-lo)
            body += f'<rect x="{75+a*28}" y="{320-b*26}" width="23" height="21" fill="hsl(174 48% {light:.1f}%)"><title>{c["q"]}: {c["objective"]:.3f}</title></rect>'
        a, b = case['best']['q']
        body += f'<rect x="{73+a*28}" y="{318-b*26}" width="27" height="25" fill="none" stroke="#bc482d" stroke-width="3"/><text x="53" y="340">0</text><text x="39" y="70">10</text><text x="348" y="373">10</text><text x="200" y="407">チャネルAへの配分</text><text x="220" y="90">濃いほど目的値が小さい</text><text x="235" y="120">A+B ≤ 10</text>'
        best = case['best']
        frames.append(svg(body, f'容量10、リスク重み{case["weight"]}、最適配分{best["q"]}', 425)+f'<p><strong>配分 {best["q"]}、平均費用 {best["mean"]:.3f}、CVaR₀.₈ {best["tail"]:.3f}</strong></p><p>赤枠は、66通りの中で平均費用と高い方20%の平均費用を重みづけした値が最小の配分。w={case["weight"]:.2f}、重みづけ後の値 {best["objective"]:.3f}。色の濃さは同じ画面の中だけで比べる。</p>')
        options.append(f'w={case["weight"]:.2f}')
    out = select_figure('費用が高い場合を重く見ると、在庫をどちらに置くか', '高い方20%の費用を重く見る度合い（w）', options, frames,
                         'w=0なら平均費用だけ、w=1なら費用が高い方20%の平均（CVaR₀.₈）だけを見る。Labでは同じ確率の需要10通りを使うため、高い方2件に当たる。境界に同じ費用が並ぶ場合も、合計20%になるよう重みづけする。論文では高い方10%（CVaR₀.₉）を使う。<a href="https://hbemdata.org/index.php/ojs/article/download/198/176">原典§3.2式(4)・§4.4</a>。どの重みでも同じ合成需要で整数の配分を比べる。著者の学習や、配分を微分して学習に戻す処理は再現していない。')
    body = '<path d="M60 35V290H480" stroke="currentColor" fill="none"/>'
    for key, color in [('true','#137d79'), ('naive','#b85236'), ('masked','#355baa')]:
        points = ' '.join(f'{60+c["q"]*27},{290-c[key]*4}' for c in r['censoring'])
        body += f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{"6 3" if key=="masked" else "none"}"/>'
    body += '<text x="12" y="22">費用</text><text x="20" y="58">60</text><text x="44" y="312">0</text><text x="160" y="315">4</text><text x="320" y="315">10</text><text x="435" y="335">注文量</text><text x="240" y="45" fill="#137d79">緑：真の需要10</text><text x="240" y="75" fill="#b85236">赤：売上4を需要と扱う</text><text x="240" y="105" fill="#355baa">青破線：欠品を考慮</text>'
    out += f'<figure class="teaching"><h3>余剰罰則を消しても、真の需要は分からない</h3>{svg(body,"欠品を考慮した損失は発注4以上で0のまま。需要10だったとは分からない。",350)}<figcaption>在庫移送なし（ρ=0）、保有費用1、欠品費用6の例。売上4を超えた発注を余剰と扱わないため、青い破線は発注4以上（q≥4）で横ばいになる。移送がある場合の命題2までは検証していない。</figcaption></figure>'
    rows = [(name, values[0], '#b85236' if name=='PTO + CVaR' else '#137d79' if name=='RA-DFL' else '#72818f') for name, values in r['paper_evidence']['m5'].items()]
    return out + bars('M5では、同じ基準予測にCVaRを使う配分を足すと費用が9.7%増えた', rows, 6, '',
        '著者の表II。LightGBM-QRで予測してから配分する基準は4.903、同じ予測にCVaRを使う配分を合わせると5.380。RA-DFLは4.721で基準より3.7%低いが、DFL-EVの4.690より高い。')


def widget(result):
    if not isinstance(result, dict):
        return ''
    renderer = {'orpr': orpr, 'proximal': proximal, 'radfl': radfl}.get(result.get('lab02'))
    return renderer(result) if renderer else ''
