"""Human-readable reading lists from generated cards. Native browser NOT TESTED."""
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess

import pytest
from test_library_export import exported_library

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def text_library(exported_library):
    # Read labels from the real template options, never a second translation map.
    from paper_lab.build import build
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp) / 'site'
        build(root=ROOT, site_dir=site)
        class Labels(HTMLParser):
            def __init__(self):
                super().__init__(); self.name = None; self.value = None; self.labels = {}
            def handle_starttag(self, tag, attrs):
                a = dict(attrs)
                if tag == 'select': self.name = a['name']; self.labels[self.name] = {}
                if tag == 'option': self.value = a['value']; self.labels[self.name][self.value] = ''
            def handle_data(self, data):
                if self.name and self.value is not None: self.labels[self.name][self.value] += data
            def handle_endtag(self, tag):
                if tag == 'option': self.value = None
                if tag == 'select': self.name = None
        parsed = Labels(); parsed.feed((site / 'index.html').read_text())
    return dict(exported_library, labels=parsed.labels)

@pytest.mark.parametrize('mode', ['all', 'filters', 'empty', 'ime', 'navigation', 'history-failure',
    'missing-blob', 'missing-url', 'blob', 'create', 'click', 'revoke', 'repeat', 'file-origin',
    'no-window', 'multiline', 'credentials'])
def test_plain_reading_list(mode, text_library, tmp_path):
    fixture = tmp_path / 'fixture.json'; fixture.write_text(json.dumps(text_library, ensure_ascii=False))
    subprocess.run(['node', str(ROOT / 'tests/library_text_export_smoke.cjs'), str(fixture), mode], check=True)
