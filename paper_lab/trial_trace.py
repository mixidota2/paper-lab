"""Embed the standalone reviewed teaching controls without external dependencies."""
def widget(source):
    text=(source/'index.html').read_text()
    start=text.index('<h2>操作できる合成例</h2>')
    end=text.index('<h2>限界</h2>')
    html=text[start:end]
    for name in ('a','h','g','b','q','reset','out'):
        html=html.replace('id="'+name+'"','id="tt-'+name+'"')
    model=(source/'model.js').read_text()
    ui=(source/'ui.js').read_text().replace('doc.getElementById(id)',"doc.getElementById('tt-'+id)")
    return '<section id="tt-widget" aria-label="二層採点の合成例"><style>#tt-widget label{display:block;margin:1rem 0}#tt-widget select,#tt-widget button{font:inherit;max-width:100%}#tt-widget pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'+html+'<script>(function(){'+model+'\n'+ui+'})();</script></section>'
