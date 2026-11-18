"""Render a bounded, source-attributed survey; no numerical simulation."""
from datetime import date
from html import escape
from urllib.parse import urlsplit
import yaml

SLUG = 'forecast-to-replenishment'
PERIOD = {'current': '重点期間の事例', 'legacy': '旧年の比較事例'}
DOMAIN = {'retail': '販売在庫（補充・売切り）', 'maintenance': '保全補修部品'}
EVALUATION = {'backtest': '計算バックテスト', 'model': 'モデルによる企業ケース評価',
              'observational': '観察的な本番比較（非無作為）', 'randomized': '現場の無作為比較'}
FIELDS = {'task': '業務課題・分野', 'scope': '確認した規模・評価期間',
          'forecast': '予測出力・需要検閲', 'policy': '方策・制約・納期',
          'result': '著者・企業の報告値と比較条件', 'operation': '導入・計算・運用の報告',
          'limitation': '因果解釈・未確認事項'}
IDS = ('zalando', 'jd-orpr', 'amazon-rme', 'alibaba', 'jd-e2e', 'fengyi-override', 'waste-markdown')


def load_cards(path):
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'updated','checked','period_start','period_end','cards'}:
        raise ValueError('survey schema mismatch')
    checked, start, end = (date.fromisoformat(data[k]) for k in ('checked','period_start','period_end'))
    updated = date.fromisoformat(data['updated'])
    if not start <= checked <= updated <= end:
        raise ValueError('check date outside survey period')
    cards = data['cards']
    if not isinstance(cards, list) or tuple(c.get('id') for c in cards) != IDS:
        raise ValueError('exact reviewed card identities and order required')
    for c in cards:
        required = {'id','company','title','period','domain','evaluation','publication_date','material','sources','checked','comparison','followup'} | set(FIELDS)
        if set(c) != required or any(not isinstance(c[k], str) or not c[k].strip() for k in required-{'sources','comparison','followup'}):
            raise ValueError('complete textual card fields required')
        comparison = c['comparison']
        if not isinstance(comparison, dict) or set(comparison) != {'decision','connection','assessment','conditions'} or any(not isinstance(v, str) or not v.strip() for v in comparison.values()):
            raise ValueError('complete comparison fields required')
        followup = c['followup']
        if not isinstance(followup, dict) or set(followup) != {'checked','scope'} or any(not isinstance(v, str) or not v.strip() for v in followup.values()):
            raise ValueError('scoped follow-up date and source scope required')
        if not date.fromisoformat(c['checked']) <= date.fromisoformat(followup['checked']) <= updated:
            raise ValueError('follow-up date outside reviewed update')
        if c['period'] not in PERIOD or c['domain'] not in DOMAIN or c['evaluation'] not in EVALUATION:
            raise ValueError('unknown evidence classification')
        reviewed = date.fromisoformat(c['checked'])
        if reviewed > checked:
            raise ValueError('card review date exceeds survey update')
        publication = date.fromisoformat(c['publication_date'])
        if publication > reviewed or (c['period']=='current') != (start <= publication <= end):
            raise ValueError('publication date does not match period label')
        if not isinstance(c['sources'], list) or not c['sources']:
            raise ValueError('primary-source links required')
        for s in c['sources']:
            if not isinstance(s,dict) or set(s) != {'label','url'} or not all(isinstance(v,str) and v for v in s.values()):
                raise ValueError('source label and URL required')
            u = urlsplit(s['url'])
            if u.scheme != 'https' or not u.hostname or u.username or u.password:
                raise ValueError('public HTTPS source URL required')
    return data


def survey_dates(data):
    """Keep editing dates separate from historical and scoped source checks."""
    counts = {}
    for card in data['cards']:
        counts[card['checked']] = counts.get(card['checked'], 0) + 1
    history = '、'.join(f'{day}（{count}件）' for day, count in sorted(counts.items()))
    return f"ガイド更新日：{data['updated']} UTC。既存の原典確認記録：{history}。今回の再読日と範囲は事例別に表示しています。"


def render_comparison(data):
    html = '<h3 id="company-comparison">企業事例を同じ項目で比べる</h3>'
    html += '<p>評価条件が異なるため効果量の順位表ではありません。報告値と比較条件は各カードを参照してください。この表は全事例を表示し、下の絞込みはカードに適用します。</p>'
    html += '<div class="repl-comparison-scroll" role="region" aria-label="企業事例の比較表（横にスクロールできます）" tabindex="0"><table class="repl-comparison">'
    html += '<caption>対象・方式・評価と確認範囲</caption><thead><tr>'
    for label in ['企業・公表日', '対象意思決定・データ粒度', '予測との接続・手法', '評価区分・実測と推定', '導入・評価の条件', '一次出典・再読した範囲']:
        html += f'<th scope="col">{label}</th>'
    html += '</tr></thead><tbody>'
    for c in data['cards']:
        html += f'<tr data-comparison-row><th scope="row">{escape(c["company"])}<br>{escape(c["publication_date"])}<br>{escape(PERIOD[c["period"]])}</th>'
        for field in ['decision', 'connection', 'assessment', 'conditions']:
            label = escape(EVALUATION[c['evaluation']]) + '<br>' if field == 'assessment' else ''
            html += f'<td>{label}{escape(c["comparison"][field])}</td>'
        links = ' ／ '.join(f'<a href="{escape(s["url"], quote=True)}">{escape(s["label"])}</a>' for s in c['sources'])
        html += f'<td>{links}<p>部分再読日：{escape(c["followup"]["checked"])} UTC</p><p>{escape(c["followup"]["scope"])}</p></td></tr>'
    return html + '</tbody></table></div>'


def render_cards(data):
    def options(labels):
        return '<option value="all">すべて</option>'+''.join(f'<option value="{escape(k)}">{escape(v)}</option>' for k,v in labels.items())
    html = '''<section class="repl-survey" data-replenishment-survey aria-label="補充事例の比較">
<style>
.repl-comparison-scroll{max-width:100%;overflow-x:auto}.repl-comparison{min-width:1320px;table-layout:fixed;width:100%}.repl-comparison th,.repl-comparison td{vertical-align:top;overflow-wrap:anywhere}.repl-comparison th:first-child{width:10%}.repl-comparison td:last-child{width:24%}.repl-survey{margin:24px 0}.repl-survey .repl-controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr));gap:12px;background:#f0f5f2;padding:16px}.repl-survey label{display:block}.repl-survey select,.repl-survey button{font:inherit;padding:8px;max-width:100%}.repl-survey select{display:block;width:100%}.repl-survey button{margin-top:12px}.repl-survey [hidden]{display:none!important}.repl-survey .evidence-card{border:1px solid #bacdc2;border-radius:12px;padding:clamp(12px,3vw,24px);margin:16px 0;background:#fff}.repl-survey .evidence-tags{font-size:.9em;color:#375648}.repl-survey dl{margin:12px 0}.repl-survey dt{font-weight:700;margin-top:12px}.repl-survey dd{margin:4px 0 12px;overflow-wrap:anywhere}.repl-survey .evidence-card a{overflow-wrap:anywhere}.repl-survey .evidence-card h4{font-size:1.25rem;line-height:1.5}.repl-survey .repl-empty{padding:16px;background:#fff5dd}
</style>
'''
    html += f'<p data-survey-dates>{escape(survey_dates(data))}</p>' + render_comparison(data) + '<div class="repl-controls">'
    for k,label,labels in [('period','発表時期',PERIOD),('domain','対象業務',DOMAIN),('evaluation','評価の種類',EVALUATION)]:
        html += f'<label>{label}<select id="repl-{k}" data-filter="{k}">{options(labels)}</select></label>'
    html += f'</div><button type="button" data-filter-reset>絞込みを解除</button><p role="status" aria-live="polite" data-filter-count>{len(data["cards"])}件 / 全{len(data["cards"])}件</p><p class="repl-empty" data-filter-empty hidden>条件に合う事例はありません。条件を変えるか、絞込みを解除してください。</p><noscript><p>JavaScriptが無効なため全事例を表示しています。以下の年代見出しと評価区分で比較できます。</p></noscript>'
    for period,title in PERIOD.items():
        html += f'<section data-card-group="{period}"><h3>{title}</h3>'
        for c in data['cards']:
            if c['period'] != period:
                continue
            html += f'<article class="evidence-card" id="case-{c["id"]}" data-evidence-card data-period="{period}" data-domain="{c["domain"]}" data-evaluation="{c["evaluation"]}">'
            html += f'<h4>{escape(c["company"])}：{escape(c["title"])}</h4><p class="evidence-tags">{DOMAIN[c["domain"]]} ／ {EVALUATION[c["evaluation"]]}</p>'
            html += f'<p>主資料の公表日：<time datetime="{c["publication_date"]}">{c["publication_date"]}</time> ／ {escape(c["material"])}<br>既存確認記録：{escape(c["checked"])} UTC</p><dl>'
            for field,label in FIELDS.items():
                html += f'<dt>{label}</dt><dd data-field="{field}">{escape(c[field])}</dd>'
            html += '</dl><p>一次出典・読解範囲：</p><ul>'
            for s in c['sources']:
                html += f'<li><a href="{escape(s["url"],quote=True)}">{escape(s["label"])}</a></li>'
            html += '</ul></article>'
        html += '</section>'
    html += '<p><a href="../downloads/guides/replenishment-evidence.yaml" download>事例カードのデータ</a> ／ <a href="../downloads/guides/forecast-to-replenishment.md" download>比較・PoCの原稿</a></p></section><script src="../assets/replenishment-filter.js" defer></script>'
    return html
