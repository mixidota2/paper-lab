"""Render the paper's local, dependency-free teaching experiment."""


def widget(source):
    html = (source / "widget.html").read_text(encoding="utf-8")
    data = (source / "results.json").read_text(encoding="utf-8").replace("<", "\\u003c")
    js = (source / "interactive.js").read_text(encoding="utf-8")
    return f'{html}<script type="application/json" id="dcdn-data">{data}</script><script>{js}</script>'
