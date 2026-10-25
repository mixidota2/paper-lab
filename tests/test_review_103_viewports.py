"""Source wiring checks only; no browser screenshots are simulated as evidence."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class ViewportWiringTests(unittest.TestCase):
    def setUp(self):
        self.tree=ast.parse((ROOT/'tests/review_103.py').read_text())
        self.functions={n.name:n for n in ast.walk(self.tree) if isinstance(n,ast.FunctionDef)}

    def test_capture_is_one_bounded_viewport(self):
        node=self.functions['viewport_snapshot']
        screenshots=[n for n in ast.walk(node) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='screenshot']
        self.assertEqual(len(screenshots),1)
        kw={k.arg:ast.literal_eval(k.value) for k in screenshots[0].keywords if k.arg in ('full_page','timeout')}
        self.assertEqual(kw,{'full_page':False,'timeout':5000})
        self.assertFalse(any(isinstance(n,(ast.For,ast.While)) for n in ast.walk(node)))
        text=ast.unparse(node)
        self.assertIn('viewport-only.png',text)
        self.assertIn('below-fold content not captured',text)
        self.assertIn('NOT TESTED',text)

    def test_library_capture_precedes_search_and_is_width_limited(self):
        node=self.functions['library_search'];text=ast.unparse(node)
        capture=next(n for n in node.body if isinstance(n,ast.If) and 'viewport_snapshot' in ast.unparse(n))
        self.assertEqual(ast.unparse(capture.test),'width in (360, 1440)')
        self.assertEqual(ast.unparse(capture.body[0]),'guard(browser)')
        self.assertLess(text.index('viewport_snapshot'),text.index("fill('2609.04518')"))
        self.assertIn('library-initial-',text)

    def test_proximal_capture_precedes_interaction_and_has_exact_scope(self):
        node=self.functions['visit'];text=ast.unparse(node)
        capture=next(n for n in node.body if isinstance(n,ast.If) and 'viewport_snapshot' in ast.unparse(n))
        self.assertEqual(ast.unparse(capture.test),"width in (360, 1440) and path.stem == 'proximal-residual-value-inventory-placement'")
        self.assertEqual(ast.unparse(capture.body[0]),'guard(browser)')
        self.assertLess(text.index('viewport_snapshot'),text.index('explorer_checks'))

    def test_only_two_capture_call_sites(self):
        calls=[n for n in ast.walk(self.tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='viewport_snapshot']
        self.assertEqual(len(calls),2)
        self.assertTrue(all(ast.unparse(n.args[0])=='page' for n in calls))


if __name__=='__main__':unittest.main()
