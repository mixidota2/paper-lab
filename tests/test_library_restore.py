"""Saved reading-list filter restoration, including interrupted file reads."""
import json
from pathlib import Path
import subprocess
import pytest
from test_library_export import exported_library
ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('mode', [
 'roundtrip','fullwidth','zero','bom','file-origin','history-failure','no-window','missing-url','untrusted-extra',
 'invalid-json','invalid-null','invalid-array','invalid-kind','invalid-version','invalid-missing','invalid-extra-filter',
 'invalid-filter-type','invalid-array-filters','invalid-topic','invalid-verdict','invalid-sort','invalid-size',
 'invalid-size-negative','invalid-size-nan','invalid-body-size','invalid-prototype',
 'read-error','read-unsupported','read-nonstring','pending-new-file','pending-old-error','pending-edit','pending-change',
 'pending-reset','pending-submit','pending-compose','pending-popstate','pending-pageshow','pending-history-pageshow','pending-native-cancel','pending-cancel','ime','repeat','preserve-url',
])
def test_restore_saved_reading_filters(mode, exported_library, tmp_path):
    fixture = tmp_path / 'fixture.json'
    fixture.write_text(json.dumps(exported_library, ensure_ascii=False))
    subprocess.run(['node', str(ROOT / 'tests/library_restore_smoke.cjs'), str(fixture), mode], check=True)


def test_restore_control_explains_current_results(tmp_path):
    from paper_lab.build import build
    from html.parser import HTMLParser
    site = tmp_path / 'site'
    build(root=ROOT, site_dir=site)
    html = (site / 'index.html').read_text()
    class Fields(HTMLParser):
        def __init__(self):
            super().__init__(); self.nodes = []
        def handle_starttag(self, tag, attrs):
            self.nodes.append((tag, dict(attrs)))
    fields = Fields(); fields.feed(html)
    input_tag, attrs = next((tag, a) for tag, a in fields.nodes if 'data-reading-import' in a)
    assert input_tag == 'input' and attrs['type'] == 'file'
    assert attrs['accept'] == '.json,application/json'
    assert any(tag == 'label' and a.get('for') == attrs['id'] for tag, a in fields.nodes)
    assert any(a.get('id') == attrs['aria-describedby'] for tag, a in fields.nodes)
    assert any(a.get('role') == 'status' for tag, a in fields.nodes if 'data-reading-import-status' in a)
    assert '現在のLabから選び直すため' in html
    assert 'サーバーへ送信しません' in html
