"""Offline contracts only; fake CSSOM is not browser execution evidence."""
import base64
from pathlib import Path
import struct
import tempfile
import unittest
from review_measurements import assert_percent_width
from review_capture import capture_segments

class Width:
    def __init__(self, actual, canonical='33.3333%'):
        self.actual=actual; self.canonical=canonical; self.received=None
    def evaluate(self, expression, expected):
        self.received=expected
        assert 'document.createElement' in expression
        assert 'probe.style.width = `${expected}%`' in expression
        return {'actual':self.actual,'expected':self.canonical}

class Footer:
    def __init__(self,page):self.page=page
    def bounding_box(self):
        return {'x':12,'y':21580.28125-self.page.y,'width':321,'height':120.78125+self.page.footer_extra}
    def is_visible(self):return True
class Session:
    def __init__(self,page):self.page=page
    def send(self,*args):
        # Header accepted by the existing dimension checker; no rendered pixels.
        return {'data':base64.b64encode(b'\x89PNG\r\n\x1a\n'+b'0'*8+struct.pack('>II',360,900)+str(self.page.y).encode()).decode()}
    def detach(self):pass
class Page:
    url='fixture://fractional-footer'
    def __init__(self,margin=1,footer_extra=0):
        self.y=0;self.total=21701+margin;self.footer_extra=footer_extra;self.context=self
    def new_cdp_session(self,page):return Session(self)
    def locator(self,selector):return Footer(self)
    def wait_for_timeout(self,n):pass
    def evaluate(self,expression,arg=None):
        if 'document.images' in expression:return True
        if 'document.fonts' in expression:return True
        if 'createTreeWalker' in expression:return {'innerWidth':360,'clientWidth':345,'scrollWidth':345,'height':self.total,'viewportHeight':900,'textRects':1,'rightmostText':333,'bad':[]}
        if 'window.scrollTo' in expression:
            self.y=min(arg or 0,self.total-900);return
        if '({x:scrollX' in expression:return {'x':0,'y':self.y,'width':360,'height':900,'total':self.total,'clientWidth':345}
        raise AssertionError(expression)

class Regression(unittest.TestCase):
    def test_stock_selector_source_contract(self):
        source=(Path(__file__).with_name('review_103.py')).read_text()
        self.assertIn("stock_rows=page.locator('#bars > p').filter(has_text='棚在庫')",source)
        self.assertIn('assert stock_rows.count()==len(active)',source)
        self.assertIn('assert stock_bar.count()==required_bar.count()==1',source)
        self.assertNotIn("widths=page.locator('#bars .bar')",source)

    def test_cssom_canonical_match(self):
        width=Width('33.3333%');assert_percent_width(width,100/3)
        self.assertEqual(width.received,100/3)
    def test_cssom_rejects_mutations(self):
        for actual in ['33.3334%','33.3%','33.3333px','','100%','0%']:
            with self.subTest(actual=actual),self.assertRaises(AssertionError):assert_percent_width(Width(actual),100/3)
    def test_invalid_expected(self):
        for value in [float('nan'),float('inf'),-1]:
            with self.subTest(value=value),self.assertRaises(AssertionError):assert_percent_width(Width(''),value)
    def test_full_footer_reached_with_real_margin(self):
        with tempfile.TemporaryDirectory() as d:
            capture_segments(Page(),Path(d)/'capture.png')
            import json
            report=json.loads((Path(d)/'capture/segments.json').read_text())
            self.assertEqual(report['tiles'][-1]['y'],20802)
            footer=report['footer'];self.assertLessEqual(footer['y']+footer['height'],900)
            self.assertEqual(footer['y']+footer['height'],899.0625)
    def test_no_clearance_still_fails_clipping(self):
        with tempfile.TemporaryDirectory() as d,self.assertRaises(AssertionError):capture_segments(Page(margin=0),Path(d)/'capture.png')
    def test_footer_overflow_mutation_fails(self):
        with tempfile.TemporaryDirectory() as d,self.assertRaises(AssertionError):capture_segments(Page(footer_extra=2),Path(d)/'capture.png')
    def test_old_early_stop_was_one_pixel_short(self):
        self.assertTrue(20800+900 >= 21701-1)
        self.assertFalse(20800+900 >= 21701)
        self.assertEqual(21580.28125-20800+120.78125,901.0625)

if __name__=='__main__':unittest.main()
