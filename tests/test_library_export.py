"""Reading-list snapshots use generated cards; native downloads are NOT TESTED."""
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess

import pytest
from paper_lab.build import build
from test_library_navigation import LibraryHTML

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def exported_library(tmp_path_factory):
    site = tmp_path_factory.mktemp('reading-list') / 'site'
    build(root=ROOT, site_dir=site)
    html = (site / 'index.html').read_text()
    parsed = LibraryHTML(html)
    class Cards(HTMLParser):
        def __init__(self):
            super().__init__(); self.rows = []; self.row = None; self.capture = None; self.fields = set()
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            self.fields.update(k for k in a if k.startswith('data-reading-'))
            if 'data-paper' in a:
                self.row = dict(dataset={k[5:]:v for k,v in a.items() if k.startswith('data-')}, title='', question='', href='')
                self.rows.append(self.row)
            if self.row and tag == 'a' and not self.row['href']:
                self.row['href'] = a['href']; self.capture = 'question'
            if self.row and tag == 'p' and a.get('class') == 'paper-title': self.capture = 'title'
        def handle_endtag(self, tag):
            if tag in ('a','p'): self.capture = None
            if tag == 'article': self.row = None
        def handle_data(self, data):
            if self.capture: self.row[self.capture] += data
    cards = Cards(); cards.feed(html)
    return dict(cards=cards.rows, defaults=parsed.defaults, options=parsed.options,
                fields=sorted(cards.fields), source=(site / 'assets/library.js').read_text())


@pytest.mark.parametrize('mode', ['all', 'filters', 'empty', 'ime', 'navigation', 'history-failure',
    'missing-blob', 'missing-url', 'blob', 'create', 'click', 'revoke', 'repeat', 'file-origin', 'no-window'])
def test_reading_list_snapshot(mode, exported_library, tmp_path):
    fixture = tmp_path / 'fixture.json'; fixture.write_text(json.dumps(exported_library, ensure_ascii=False))
    subprocess.run(['node', str(ROOT / 'tests/library_export_smoke.cjs'), str(fixture), mode], check=True)
