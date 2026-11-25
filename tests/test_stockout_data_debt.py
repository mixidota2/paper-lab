from fractions import Fraction as F
from itertools import product
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'papers'/'stockout-data-debt'
spec=importlib.util.spec_from_file_location('stockout_data_debt',P/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TestStockoutDataDebt(unittest.TestCase):
    def test_artifact_is_reproducible(self):
        self.assertEqual(json.loads((P/'results.json').read_text()),json.loads(json.dumps(m.results())))
    def test_figure1_exact_endpoints(self):
        self.assertEqual(m.demand_interval(11),(F(1,4),F(3,4)))
        self.assertEqual(m.one_cost(F(1,4),0)-m.one_cost(F(1,4),1),F(1,4))
        self.assertEqual(m.one_cost(F(3,4),1)-m.one_cost(F(3,4),0),F(1,4))
    def test_noninformative_gamma(self):
        self.assertEqual(m.demand_interval(1),(F(1,2),F(1,2)))
        self.assertEqual(m.one(1)['worst_regret'],[0,0])
    def test_compatible_completions_and_monotone_debt(self):
        prev=0
        for g in m.GAMMAS:
            lo,hi=m.demand_interval(g)
            for p in (lo,hi):
                w=(p-F(1,5))/F(3,5)
                self.assertTrue(F(1,g)<=w/(1-w)<=g)
                self.assertEqual(F(1,5)+F(1,5)+F(3,5),1)
            r=m.one(g);self.assertGreaterEqual(r['data_debt'],prev);prev=r['data_debt']
    def test_figure2_full_enumeration(self):
        r=m.carryover()
        self.assertEqual(r['data_debt'],.1225)
        self.assertEqual(r['chosen_policy'],(1,0,0))
        self.assertEqual(r['worst_regret'][0],.1775)
    def test_grid_matches_proposition_and_dominance(self):
        c=F(7,10);a,b=F(7,20),F(13,20)
        for i,j in product(range(21),repeat=2):
            t=a+(b-a)*F(i,20);u=a+(b-a)*F(j,20)
            self.assertEqual(m.two_cost(t,u,(0,0,0)),t+u)
            self.assertEqual(m.two_cost(t,u,(1,0,0)),c+t*u)
            costs=[m.two_cost(t,u,p) for p in product((0,1),(0,1),(0,))]
            self.assertEqual(min(costs),min(t+u,c+t*u))
            self.assertLessEqual(m.two_cost(t,u,(1,0,0))-min(costs),F(49,400))
            self.assertGreater(c,t);self.assertGreater(c,u)
    def test_reject_invalid_inputs(self):
        with self.assertRaises(ValueError):m.demand_interval(.5)
        with self.assertRaises(ValueError):m.two_cost(F(1,2),F(1,2),(1,1,1))
    def test_evidence_is_not_a_store_trial(self):
        y=(P/'lab.yaml').read_text()
        for text in ('実店舗の発注変更による効果は報告していません','27通り','30組','3設定で大きく','Γの妥当性'):
            self.assertIn(text,y)
if __name__=='__main__':unittest.main()
