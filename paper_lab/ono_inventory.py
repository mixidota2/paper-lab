"""Render the reported paired comparisons separately from an invented service example."""
from html import escape


def widget(results):
    markup = [
        '<div id="ono-lab" class="card">',
        '<h3>欠品費用を変えると、在庫費用の差はどこまで広がるか</h3>',
        '<p>欠品1個の費用を商品価格の何%に置くか、条件を1つ開いてください。'
        '表7の報告値を使っています。論文にない条件は計算しません。</p>',
    ]
    for i, row in enumerate(results["reported_table7"]):
        penalty, cfms, ses, delta, pct = (row[key] for key in
            ("shortage_pct", "cfms", "ses", "difference", "reduction_pct"))
        initial = " open" if i == 0 else ""
        markup.append(
            f'<details name="ono-penalty"{initial}><summary>商品価格の{penalty:g}%</summary>'
            f'<p>総費用：CFMS {cfms:,}、SES {ses:,}。'
            f'CFMSの方が{delta:,}（SESの費用の{pct:.2f}%）低い結果でした。</p></details>'
        )
    markup.extend([
        '<h3>欠品数量が同じでも、欠品した回数は変わる</h3>',
        '<p>ここからは人工例です。10回の補充サイクルで毎回10個の需要があり、'
        '合計100個のうち96個を在庫で満たします。足りない4個をどう分けるかで、'
        '欠品のないサイクルの割合はどう変わるでしょうか。</p>',
        '<p>各サイクルで満たせた個数を順に表示します。</p>',
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
