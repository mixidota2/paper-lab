"""Render only this Lab's self-authored controls and scripts."""
def widget(source):
    html = (source / 'interactive.html').read_text(encoding='utf-8')
    scripts = '\n'.join((source / f).read_text(encoding='utf-8') for f in ('model.js', 'interactive.js'))
    return html + '<script>' + scripts + '</script>'
