"""Only this Lab's self-authored widget; published rounded table is embedded data."""
def widget(source):
    table=(source/'table3.json').read_text(encoding='utf-8').replace('<','\\u003c')
    html=(source/'interactive.html').read_text(encoding='utf-8')
    scripts='\n'.join((source/name).read_text(encoding='utf-8') for name in ('model.js','interactive.js'))
    return html+'<script type="application/json" id="scv-table-data">'+table+'</script><script>'+scripts+'</script>'
