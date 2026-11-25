"""Render the reported paired comparisons separately from an invented service example."""
from html import escape


def widget(results):
    markup = [
        '<div id="ono-lab" class="card">',
        '<h3>欠品費用の条件ごとの比較</h3>',
        '<p>条件を開くと、欠品1個の費用を商品価格の何%としたかに応じて、論文が報告した総費用を比べられます。'
        '表示するのは表7の報告値です。論文にない条件は計算しません。</p>',
    ]
    for i, row in enumerate(results["reported_table7"]):
        penalty, cfms, ses, delta, pct = (row[key] for key in
            ("shortage_pct", "cfms", "ses", "difference", "reduction_pct"))
        initial = " open" if i == 0 else ""
        markup.append(
            f'<details name="ono-penalty"{initial}><summary>商品価格の{penalty:g}%</summary>'
            f'<p>総費用：CFMS {cfms:,}、SES {ses:,}。'
            f'CFMSの総費用はSESより{delta:,}低くなりました。SESの総費用を基準に{pct:.2f}%の差です。</p></details>'
        )
    markup.extend([
        '<h3>欠品が起きるサイクル数と欠品数量</h3>',
        '<p>次の人工例では、10回の補充サイクルで毎回10個の需要があるとします。'
        '店は合計100個のうち96個を在庫で満たします。'
        '足りない4個が一度に出る場合と、複数のサイクルに分かれる場合を比べます。</p>',
        '<p>条件を開くと、各サイクルで在庫から満たせた個数を順に確認できます。</p>',
    ])
    for i, row in enumerate(results["toy_service"]):
        label = escape(row["label"])
        sequence = "、".join(map(str, row["served"]))
        initial = " open" if i == 0 else ""
        markup.append(
            f'<details name="ono-service"{initial}><summary>{label}</summary>'
            f'<p>各サイクルで在庫から満たせた個数：{sequence}</p>'
            f'<p>欠品のなかったサイクルの割合：<strong>{row["csl_pct"]:g}%</strong>。'
            f'在庫で満たせた数量の割合：<strong>{row["fill_pct"]:g}%</strong>。</p></details>'
        )
    return "\n".join(markup + ["</div>"])
