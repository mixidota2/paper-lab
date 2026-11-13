"""Initial line-series data stays readable without JS. Static HTML, not browser QA."""
from html.parser import HTMLParser
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
import pytest
import yaml

from paper_lab.build import build
from paper_lab.display_labels import explorer_axes, explorer_view

ROOT = Path(__file__).resolve().parents[1]
SAVED = sorted(path for path in (ROOT / 'papers').glob('*/results.json')
               if isinstance(data := json.loads(path.read_text()), dict) and data.get('explorer'))


class Node:
    def __init__(self, tag='', attrs=None):
        self.tag, self.attrs, self.children, self.parts = tag, dict(attrs or []), [], []

    @property
    def text(self):
        return ''.join(self.parts)

    def find(self, tag=None, attr=None):
        found = [self] if (tag is None or self.tag == tag) and (attr is None or attr in self.attrs) else []
        return found + [result for child in self.children for result in child.find(tag, attr)]


class Tree(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return

    def handle_data(self, text):
        for node in self.stack:
            node.parts.append(text)


def assert_table(table, frame, axes):
    lines = frame['lines']
    expected_headers = [axes['label'] if axes else '点'] + [line['label'] for line in lines]
    head, = table.find('thead')
    assert [n.text for n in head.find('th')] == expected_headers
    assert all(n.attrs.get('scope') == 'col' for n in head.find('th'))
    body, = table.find('tbody')
    rows = body.find('tr')
    assert len(rows) == max(len(line['values']) for line in lines)
    for i, row in enumerate(rows):
        heading, = row.find('th')
        assert heading.attrs.get('scope') == 'row'
        assert heading.text == str(i + (axes['start'] if axes else 1))
        actual = [cell.text for cell in row.find('td')]
        expected = ['—' if i >= len(line['values']) else '推定不能' if line['values'][i] is None
                    else str(line['values'][i]) for line in lines]
        assert actual == expected
    assert table.find('caption')[0].text == '初期条件の系列データ'


@pytest.fixture(scope='module')
def site(tmp_path_factory):
    output = tmp_path_factory.mktemp('explorer-fallback') / 'site'
    build(root=ROOT, site_dir=output)
    return output


@pytest.mark.parametrize('path', SAVED, ids=lambda p: p.parent.name)
def test_saved_initial_series_are_available_without_javascript(site, path):
    slug = path.parent.name
    data = explorer_view(slug, json.loads(path.read_text())['explorer'])
    frame = data['frames'][data['default']]
    tree = Tree((site / 'papers' / f'{slug}.html').read_text())
    sections = [node for node in tree.root.find('section') if node.attrs.get('data-interactive') == 'explorer']
    config = yaml.safe_load((path.parent / 'lab.yaml').read_text())
    expected_sections = [item for item in config.get('interactives', []) if item['kind'] == 'explorer']
    assert len(sections) == len(expected_sections), f'{slug}: mismatched explorer sections'
    for section in sections:
        fallback, = section.find(attr='data-fallback')
        assert 'hidden' not in fallback.attrs
        tables = fallback.find('table', 'data-initial-lines')
        if not frame.get('lines'):
            assert not tables
            continue
        table, = tables
        assert_table(table, frame, explorer_axes(slug))
        details, = fallback.find('details')
        assert 'open' not in details.attrs
        assert details.find('summary')[0].text == '初期条件の系列を表で読む'
        region, = details.find(attr='tabindex')
        assert region.attrs.get('role') == 'region'
        assert region.attrs.get('tabindex') == '0'
        assert region.attrs.get('aria-label') == '初期条件の系列データ'
        assert '条件を切り替えるにはJavaScriptが必要です。' in details.text
        assert (explorer_axes(slug) or {}).get('caption', '') in details.text


@pytest.mark.parametrize('path', SAVED, ids=lambda p: p.parent.name)
def test_saved_dataset_template_uses_initial_frame(path):
    slug = path.parent.name
    data = explorer_view(slug, json.loads(path.read_text())['explorer'])
    frame = data['frames'][data['default']]
    env = Environment(loader=FileSystemLoader(ROOT / 'paper_lab/templates'), autoescape=select_autoescape(['html']))
    html = env.get_template('explorer_fallback.html').render(frame=frame, explorer_axes=explorer_axes(slug))
    tree = Tree(html)
    if frame.get('lines') and any(line['values'] for line in frame['lines']):
        table, = tree.root.find('table', 'data-initial-lines')
        assert_table(table, frame, explorer_axes(slug))
    else:
        assert html == ''


@pytest.mark.parametrize('axes', [None, {'start': -2, 'label': '時点 <&>', 'caption': '日本語 <img src=x> & 条件'}])
def test_null_uneven_precise_and_escaped_series(axes):
    frame = {'value': 1, 'lines': [
        {'label': '<script>alert(1)</script>', 'values': [0, None, 0.123456789123456, -1e-12]},
        {'label': '空の系列 & "quote"', 'values': []},
        {'label': '短い系列', 'values': [5e-324]},
    ]}
    before = json.dumps(frame)
    env = Environment(loader=FileSystemLoader(ROOT / 'paper_lab/templates'), autoescape=select_autoescape(['html']))
    html = env.get_template('explorer_fallback.html').render(frame=frame, explorer_axes=axes)
    tree = Tree(html)
    table, = tree.root.find('table', 'data-initial-lines')
    assert_table(table, frame, axes)
    assert not tree.root.find('script') and not tree.root.find('img')
    assert json.dumps(frame) == before


@pytest.mark.parametrize('lines', [None, [], [{'label': 'empty', 'values': []}]])
def test_no_empty_series_control(lines):
    frame = {} if lines is None else {'lines': lines}
    env = Environment(loader=FileSystemLoader(ROOT / 'paper_lab/templates'), autoescape=select_autoescape(['html']))
    html = env.get_template('explorer_fallback.html').render(frame=frame, explorer_axes=None)
    assert html == ''
