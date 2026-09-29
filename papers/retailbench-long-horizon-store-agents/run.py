"""Deterministic teaching experiment; not the RetailBench simulator or an LLM run."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def simulate(quality_aware, active_products, days=30):
    # Artificial two suppliers; identical demand, shelf capacity, and rent.
    unit_cost, return_rate = (4, 0.3) if not quality_aware else (5, 0.05)
    cash = 3000.0
    trace = []
    for day in range(1, days + 1):
        # Ten units of demand per managed product; at most 40 shelf positions.
        sold = min(active_products, 40) * 10
        revenue = sold * 10 * (1 - return_rate)
        procurement = sold * unit_cost
        cash += revenue - procurement - 600
        trace.append({'day': day, 'cash': round(cash, 2), 'sold': sold})
    return {'supplier': 'QualityFirst' if quality_aware else 'PriceFirst',
            'final_cash': round(cash, 2), 'trace': trace}


def main():
    reported = [
        ['DeepSeek-V4-Pro', 'Plan-and-Act', 180, 10120.90, 164417],
        ['GLM-5.1', 'ReAct', 60, -2134.36, 7016],
        ['GPT-5.5', 'ReAct', 180, 24350.98, 136405],
        ['Grok-4.3', 'ReAct', 58, 828.40, 11305],
        ['Kimi-K2.6', 'ReAct', 130, 792.19, 86214],
        ['MiniMax-M2.5', 'Plan-and-Act', 73, -397.95, 23521],
        ['Qwen3.5-397B-A17B', 'Reflection', 71, 1183.17, 35622],
        ['Oracle Policy', 'Oracle', 180, 131510.42, 267998],
    ]
    frames = [{'products': n, 'policies': [simulate(False, n), simulate(True, n)]} for n in [1, 8, 20, 38]]
    assert all(f['policies'][1]['final_cash'] > f['policies'][0]['final_cash'] for f in frames)
    # Independent accounting identity, across every simulated day and setting.
    for f in frames:
        for p in f['policies']:
            margin = 4.5 if p['supplier'] == 'QualityFirst' else 3
            assert all(abs(t['cash'] - (3000 + t['day'] * (f['products']*10*margin-600))) < 1e-8 for t in p['trace'])
    result = {'lab30_retailbench': True, 'status': 'PARTIAL',
              'source': {'paper': '2603.16453v3', 'locator': 'Table 1; Section 4.3; Figure 3'},
              'reported_columns': ['model', 'framework', 'days', 'net_worth', 'sales_units'],
              'reported': reported, 'frames': frames,
              'verification': {'accounting_identity': 'CONFIRMED', 'retailbench_reproduction': 'NOT TESTED'},
              'limitations': ['Artificial deterministic inputs; no LLM, lead time, aging, news, or bankruptcy termination.', 'Final cash is not paper net worth; return rates are invented teaching assumptions.']}
    (ROOT/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('CONFIRMED: 240 daily accounting checks; RetailBench performance NOT TESTED')

if __name__ == '__main__':
    main()
