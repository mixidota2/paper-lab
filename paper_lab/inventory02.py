"""October 2 paper-specific views, generated exclusively from results.json."""
import json
from html import escape


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
            body += f'<circle cx="{x(c["loss"]):.2f}" cy="{y(c["stock"]):.2f}" r="4" fill="{color}"><title>{c["days"]}日、在庫{c["stock"]:.2f}、売り逃し{c["loss"]:.2f}</title></circle>'
        best = case['best']
        if best:
            body += f'<circle cx="{x(best["loss"]):.2f}" cy="{y(best["stock"]):.2f}" r="9" fill="none" stroke="#102d47" stroke-width="3"/>'
            text = f'選択：カテゴリA {best["days"][0]}日、B {best["days"][1]}日。累計在庫 {best["stock"]:.2f}、売り逃し {best["loss"]:.2f}。'
        else:
            text = '実行可能な候補なし。初日の未入荷による売り逃しを、この候補集合では避けられない。'
        body += f'<text x="65" y="25">累計在庫（単価1）</text><text x="275" y="335">売り逃し（単価1）</text><text x="48" y="312">0</text><text x="440" y="312">{max_loss:.0f}</text><text x="12" y="52">{max_stock:.0f}</text>'
        frames.append(svg(body, text)+f'<p><strong>{text}</strong></p><p>許容損失 {case["budget"]:.2f}、実行可能 {case["feasible"]}/100候補。緑が制約内、灰が制約外。輪が選んだラベル。</p>')
        options.append(f'αloss={case["alpha"]:.2f}')
    out = select_figure('在庫日数のラベルを選ぶ：許容損失を厳しくする', '式(2)のαloss', options, frames,
                        'Labの合成需要。縦線より左が制約内。原論文§3.3の形式に対応し、JDの再現ではない。')
    frames = []
    labels = [('回転日数 TT', '日', 6), ('在庫あり日率', '% / pp', 3), ('保有費用', '% / pp', 32)]
    for j, (label, unit, limit) in enumerate(labels):
        vals = [r['paper_evidence']['field'][key][j] for key in ['psm', 'did']]
        body = '<path d="M260 20V180" stroke="currentColor"/>'
        for i, (v, name) in enumerate(zip(vals, ['PSM A/B', 'DiD'])):
            end = 260 + 185*v/limit
            body += f'<text x="15" y="{48+i*80}">{name}</text><rect x="{min(end,260):.2f}" y="{60+i*80}" width="{abs(end-260):.2f}" height="24" fill="#137d79"/><text x="340" y="{48+i*80}">{v:+.2f}</text>'
        body += '<text x="250" y="210">0</text>'
        note = ['両方とも日数の差。PSMとDiDは異なる比較で、独立した2回の実験ではない。',
                'PSMは原表の+2.29%表記を維持。DiDは率の差+0.47ppとして読む。同一尺度の厳密な比較を意図しない。',
                'PSMは対照比−29.95%。DiDは前年比+22.05%と+3.70%の差−18.35pp。前年比での保有費用減少ではない。'][j]
        frames.append(svg(body, f'{label}: PSM {vals[0]}, DiD {vals[1]}', 230)+f'<p><strong>{label}（{unit}）</strong>。{note}</p>')
    return out + select_figure('現場の数値は、比較基準と単位ごとに読む', '表示指標', [x[0] for x in labels], frames,
        '著者の表3–4。マネジャー選定・PSM・約30日・菓子3カテゴリ。欠品費用は現場評価から除外。')


def proximal(r):
    names = {'counterexample': '図3：PCSPを満たさない強凸関数', 'state': '縮約：PWL＋状態potential', 'action': '縮約：PWL＋行動正則化'}
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
        frames.append(svg(body, f'{names[c["kind"]]}、{c["count"]}回、最終在庫{final}', 425)+f'<p><strong>最終在庫 ({final})、TV={c["tv"]:.6f}</strong></p><p>緑線：順次配置。赤い輪：同じ目的の一括配置。TV = 最終在庫のL1差 / (2×入荷量)。需要・費用変化なし。</p>')
        options.append(f'{names[c["kind"]]} / K={c["count"]}')
    out = select_figure('図3の反例を動かす：先に置いた在庫は戻せない', '目的と分割回数', options, frames,
                         '図3・付録C.1の反例は原式どおり。状態potentialと行動正則化はLab独自の分離可能な比較例。')
    rows = [(name, values[0], '#137d79' if name=='State-prox' else '#72818f') for name, values in r['paper_evidence']['oos'].items()]
    return out + bars('未知商品・別期間：State-proxは0.950、neural RLは1.012', rows, 1.2, '',
        '著者の表1、正規化SCPUTの平均。標準偏差は根拠の表を参照。オフラインのみ。図4のK=500感度は別条件で、TV 0.00201対0.12716。')


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
        body += f'<rect x="{73+a*28}" y="{318-b*26}" width="27" height="25" fill="none" stroke="#bc482d" stroke-width="3"/><text x="53" y="340">0</text><text x="39" y="70">10</text><text x="348" y="373">10</text><text x="200" y="407">チャネルAへの配分</text><text x="220" y="90">濃いほど目的が小さい</text><text x="235" y="120">A+B ≤ 10</text>'
        best = case['best']
        frames.append(svg(body, f'容量10、リスク重み{case["weight"]}、最適配分{best["q"]}', 425)+f'<p><strong>配分 {best["q"]}、平均費用 {best["mean"]:.3f}、CVaR₀.₈ {best["tail"]:.3f}</strong></p><p>赤枠は全探索の最小点。w={case["weight"]:.2f}、目的値 {best["objective"]:.3f}。色は各画面の最小〜最大で正規化し、画面間の色の濃さは比較しない。</p>')
        options.append(f'w={case["weight"]:.2f}')
    out = select_figure('容量三角形の中で、平均と裾を配分へ反映する', 'CVaRの重み', options, frames,
                         'Labの合成シナリオ・整数配分。微分可能層と学習の再現ではない。全条件で同じ需要分布を使う。')
    body = '<path d="M60 35V290H480" stroke="currentColor" fill="none"/>'
    for key, color in [('true','#137d79'), ('naive','#b85236'), ('masked','#355baa')]:
        points = ' '.join(f'{60+c["q"]*27},{290-c[key]*4}' for c in r['censoring'])
        body += f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{"6 3" if key=="masked" else "none"}"/>'
    body += '<text x="12" y="22">費用</text><text x="20" y="58">60</text><text x="44" y="312">0</text><text x="160" y="315">4</text><text x="320" y="315">10</text><text x="435" y="335">注文量</text><text x="240" y="45" fill="#137d79">緑：真の需要10</text><text x="240" y="75" fill="#b85236">赤：売上4を需要と扱う</text><text x="240" y="105" fill="#355baa">青破線：masked loss</text>'
    out += f'<figure class="teaching"><h3>余剰罰則を消しても、真の需要は分からない</h3>{svg(body,"売上4を超えるとmasked lossは0。真の需要10は同定できない。",350)}<figcaption>ρ=0、h=1、b=6のLab検算。青線はq≥4で平坦。一般の横持ちを含む命題2の検証ではない。</figcaption></figure>'
    rows = [(name, values[0], '#b85236' if name=='PTO + CVaR' else '#137d79' if name=='RA-DFL' else '#72818f') for name, values in r['paper_evidence']['m5'].items()]
    return out + bars('負の結果も残す：CVaRを後付けすると費用+9.7%', rows, 6, '',
        '著者の表II。LightGBM-QR PTO 4.903 → CVaR後付け5.380。RA-DFL 4.721はPTO比−3.7%。DFL-EV 4.690より平均費用は高い。')


def widget(result):
    if not isinstance(result, dict):
        return ''
    renderer = {'orpr': orpr, 'proximal': proximal, 'radfl': radfl}.get(result.get('lab02'))
    return renderer(result) if renderer else ''
