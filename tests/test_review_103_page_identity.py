"""Focused unit contracts; no browser is launched or represented as verified."""
import ast
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SELECTOR = 'main#paper > header.paper-hero > h1'


def heading_check():
    tree = ast.parse((ROOT / 'tests/review_103.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'assert_paper_heading')
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<heading-contract>', 'exec'), namespace)
    return namespace['assert_paper_heading']


class Heading:
    def __init__(self, text='論文の問い', count=1, visible=True):
        self.text, self.n, self.visible = text, count, visible
    def count(self): return self.n
    def is_visible(self): return self.visible
    def inner_text(self):
        if self.n != 1: raise AssertionError('Ambiguous heading')
        return self.text


class Page:
    """Unit double: selector use is asserted, never evidence of browser behavior."""
    def __init__(self, heading=None, title='論文の問い | 研究ライブラリ'):
        self.heading, self.document_title = heading or Heading(), title
    def locator(self, selector):
        assert selector == SELECTOR
        return self.heading
    def title(self): return self.document_title


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.icons=[]; self.heroes=[]; self.stack=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'icon': self.icons.append(attrs)
        if tag == 'h1' and len(self.stack) >= 2:
            parent, grandparent = self.stack[-1], self.stack[-2]
            if parent[0]=='header' and 'paper-hero' in parent[1].get('class','').split() and grandparent[0]=='main' and grandparent[1].get('id')=='paper': self.heroes.append(attrs)
        if tag not in {'meta','link','img','input','br','hr','source','area','base','embed','param','track','wbr'}: self.stack.append((tag,attrs))
    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0]==tag: self.stack.pop()


class PageIdentityTests(unittest.TestCase):
    def test_matching_visible_heading(self): heading_check()(Page())
    def test_missing_heading_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'exactly one'): heading_check()(Page(Heading(count=0)))
    def test_duplicate_hero_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'exactly one'): heading_check()(Page(Heading(count=2)))
    def test_hidden_heading_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'hidden'): heading_check()(Page(Heading(visible=False)))
    def test_empty_heading_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'empty'): heading_check()(Page(Heading(text='  ')))
    def test_wrong_paper_title_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'document title'): heading_check()(Page(title='別の論文 | 研究ライブラリ'))
    def test_embedded_mapping_heading_is_not_the_page_identity(self):
        document = '<main id="paper"><header class="paper-hero"><h1>論文の問い</h1></header><article><section id="mapping"><h2>対応</h2><div><h1>Original Paper / Official Code Mapping</h1></div></section></article></main>'
        self.assertEqual(document.count('<h1>'), 2)
        self.assertEqual(len(Tags(document).heroes), 1)

    def test_paper_template_has_one_identifiable_hero(self):
        text=(ROOT/'paper_lab/templates/paper.html').read_text()
        self.assertEqual(len(Tags(text).heroes), 1)
        self.assertIn('<h1>{{ lab.question or lab.title }}</h1>', text)
        self.assertIn('<title>{{ lab.question or lab.title }} | 研究ライブラリ</title>', text)
    def test_every_top_level_template_declares_real_inline_favicon(self):
        for template in ('index','guide','paper'):
            with self.subTest(template=template):
                icons=Tags((ROOT/f'paper_lab/templates/{template}.html').read_text()).icons
                self.assertEqual(len(icons), 1)
                self.assertEqual(icons[0]['type'], 'image/svg+xml')
                self.assertTrue(icons[0]['href'].startswith('data:image/svg+xml,'))
                svg=ET.fromstring(unquote(icons[0]['href'].split(',',1)[1]))
                self.assertEqual(svg.tag, '{http://www.w3.org/2000/svg}svg')
                self.assertEqual(svg.attrib['viewBox'], '0 0 32 32')
                self.assertGreater(len(svg), 0)
    def test_all_paper_navigation_paths_use_identity_contract(self):
        tree = ast.parse((ROOT/'tests/review_103.py').read_text())
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        identity_calls = [node for node in calls if isinstance(node.func, ast.Name) and node.func.id == 'assert_paper_heading']
        self.assertEqual(sorted(node.args[0].id for node in identity_calls), ['dp', 'nojs', 'nojs', 'nojs', 'nojs', 'page', 'page', 'trace_page'])
        for name, page in [('visit','page'),('fallback','nojs'),('wrapped_detail','page'),('wrapped_fallback','nojs'),('trace_detail','trace_page'),('trace_fallback','nojs')]:
            route = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name)
            checks = [node for node in ast.walk(route) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'assert_paper_heading']
            self.assertEqual([node.args[0].id for node in checks], [page], name)
        ambiguous = [node for node in calls if isinstance(node.func, ast.Attribute) and node.func.attr == 'locator' and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 'h1']
        self.assertEqual(ambiguous, [], 'Unscoped h1 locator remains in browser review')

    def test_runtime_uses_contract_and_keeps_console_errors(self):
        text=(ROOT/'tests/review_103.py').read_text()
        self.assertIn('assert_paper_heading(page)', text)
        self.assertNotIn("page.locator('h1').inner_text()", text)
        self.assertIn("evidence.event('console-error',msg.text,p) if msg.type=='error'", text)


if __name__ == '__main__': unittest.main()
