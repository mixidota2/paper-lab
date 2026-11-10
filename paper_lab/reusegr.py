"""Render only the self-authored ReuseGR understanding experiment."""
def widget(source):
    html = (source/'interactive.html').read_text(encoding='utf-8')
    scripts = '\n'.join((source/name).read_text(encoding='utf-8') for name in ('model.js','interactive.js'))
    return html + '<script>' + scripts + '</script>'
