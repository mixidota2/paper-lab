"""配布版と同じ教材を記事に埋め込む。外部の依存関係は使わない。"""
def widget(source):
    text=(source/'index.html').read_text()
    start=text.index('<h2>条件を切り替える</h2>')
    end=text.index('<h2>限界</h2>')
    html=text[start:end]
    for name in ('a','h','g','b','q','reset','out'):
        html=html.replace('id="'+name+'"','id="tt-'+name+'"')
    model=(source/'model.js').read_text()
    ui=(source/'ui.js').read_text().replace('doc.getElementById(id)',"doc.getElementById('tt-'+id)")
    return '<section id="tt-widget" aria-label="成果と実行基盤を採点する教材"><style>#tt-widget label{display:block;margin:1rem 0}#tt-widget select,#tt-widget button{font:inherit;max-width:100%}#tt-widget pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'+html+'<script>(function(){'+model+'\n'+ui+'})();</script></section>'
