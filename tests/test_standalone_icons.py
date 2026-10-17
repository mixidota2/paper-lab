"""Icons must travel with every standalone lab, including subpath deployments."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class IconDocument(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.icons = []
        self.body_started = False
        self.feed(text)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag in ('body', 'h1', 'h2', 'h3', 'p', 'div', 'main', 'section'):
            self.body_started = True
        if tag == 'link' and 'icon' in attrs.get('rel', '').split():
            self.icons.append((attrs, self.body_started))


def assert_inline_icon(text):
    icons = IconDocument(text).icons
    assert len(icons) == 1, 'Expected exactly one favicon'
    icon, after_body = icons[0]
    assert not after_body, 'Favicon must be in the explicit or implicit head'
    assert icon.get('type') == 'image/svg+xml'
    href = icon.get('href', '')
    assert href.startswith('data:image/svg+xml,'), 'Icon must be self-contained, not origin-relative'
    svg = ET.fromstring(unquote(href.split(',', 1)[1]))
    assert svg.tag == '{http://www.w3.org/2000/svg}svg'
    assert svg.attrib.get('viewBox') == '0 0 32 32'
    assert len(svg), 'Icon must contain visible shapes'


class StandaloneIconSourceTests(unittest.TestCase):
    def test_all_standalone_source_documents_have_inline_icons(self):
        documents = [p for p in (ROOT/'papers').rglob('*.html') if '<!doctype html>' in p.read_text().lower()]
        self.assertGreaterEqual(len(documents), 3)
        for path in documents:
            with self.subTest(path=str(path.relative_to(ROOT))):
                assert_inline_icon(path.read_text())

    def test_missing_icon_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'exactly one'):
            assert_inline_icon('<!doctype html><html><title>Lab</title><h2>Lab</h2>')

    def test_root_relative_icon_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'self-contained'):
            assert_inline_icon('<link rel="icon" type="image/svg+xml" href="/favicon.ico">')

    def test_icon_in_body_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'head'):
            assert_inline_icon('<body><link rel="icon" type="image/svg+xml" href="data:image/svg+xml,">')


def test_every_generated_downloadable_html_has_inline_icon(tmp_path):
    # Full-build integration check runs under the repository's normal pytest CI.
    from paper_lab.build import build
    site = tmp_path/'site'
    build(root=ROOT, site_dir=site)
    documents = sorted((site/'downloads').rglob('*.html'))
    assert len(documents) >= 3, 'Standalone lab downloads were not generated'
    for path in documents:
        assert_inline_icon(path.read_text())
        source = ROOT/'papers'/path.relative_to(site/'downloads')
        assert path.read_bytes() == source.read_bytes(), 'HTML download must preserve its source icon and contents'


if __name__ == '__main__': unittest.main()
