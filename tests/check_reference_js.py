"""Run bounded Python/JavaScript parity checks; requires Node.js >=18, no browser."""
import copy
import json
from pathlib import Path
import random
import subprocess
from test_reference_comparisons import model, IDS, ROOT


def main():
    rng=random.Random(416)
    cases=[]
    for i in (0,1):
        m=model(i)
        for n in range(60):
            x=copy.deepcopy(m.reference_cases()['inputs'])
            if i==0:
                x.update(base=[rng.uniform(0,30) for _ in range(7)],actual=[rng.uniform(0,40) for _ in range(7)],
                         additive=[rng.uniform(-15,15) for _ in range(7)],level=[rng.uniform(-1,1) for _ in range(7)],
                         gate=rng.random(),route='Skip' if n%3==0 else 'Correct')
            else:
                x.update(price=rng.uniform(0,20),demand=rng.randint(0,50),rent=rng.uniform(0,80),cash=rng.uniform(0,100),
                         days=8,cost_a=rng.uniform(1,8),cost_b=rng.uniform(1,8),return_a=rng.random(),return_b=rng.random(),
                         mode='funded' if n%2 else 'accounting')
            cases.append({'slug':IDS[i],'inputs':x,'expected':m.evaluate(x)})
    subprocess.run(['node',str(ROOT/'tests/reference_models.cjs')],input=json.dumps(cases),text=True,check=True,cwd=ROOT)


if __name__=='__main__':main()
