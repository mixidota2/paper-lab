# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy==2.2.6", "lightgbm==4.6.0"]
# ///
"""Small constant-elasticity teaching experiment, not a Zalando replication."""
import json
from pathlib import Path
import numpy as np
import lightgbm as lgb


def financial(q, discounts, stock, price, cost, gamma, returns=0.2, vat=0.19):
    sales = np.minimum(q, stock[:, None])
    nmv = (1-returns) * sales * price[:, None] * (1-discounts) / (1+vat)
    profit = nmv-cost[:, None]*sales
    ltp = profit+(stock[:, None]-sales*(1-returns))*gamma[:, None]
    return sales, nmv, profit, ltp


def experiment(seed):
    rng = np.random.default_rng(seed)
    n, days = 400, 56
    base = rng.lognormal(1, 0.9, n)
    elasticity = rng.uniform(0.5, 3.5, n)
    discounts = np.arange(6)/10
    features, target = [], []
    for day in range(days):
        d = rng.choice(discounts, n)
        season = 1+0.2*np.sin(2*np.pi*day/7)
        mean = base*season*(1-d)**(-elasticity)
        sales = mean*rng.lognormal(-0.5*0.9**2, 0.9, n)
        features.append(np.column_stack([base, elasticity, np.full(n,season), d]))
        target.append(sales)
    x, y = np.vstack(features), np.concatenate(target)
    true = base[:,None]*(1-discounts)**(-elasticity[:,None])
    grid = np.column_stack([np.repeat(base,6),np.repeat(elasticity,6),np.ones(n*6),np.tile(discounts,n)])
    stock = np.maximum(5, base*2.5)
    price = rng.uniform(40,120,n)
    cost = price*0.2
    gamma = price*0.25
    actual = financial(true, discounts, stock, price, cost, gamma)
    oracle_choice = actual[3].argmax(axis=1)
    row = np.arange(n)
    oracle_profit = actual[2][row,oracle_choice].sum()
    records=[]
    for loss in ['regression','tweedie']:
        model=lgb.train(dict(objective=loss,tweedie_variance_power=1.5,num_leaves=15,learning_rate=0.05,monotone_constraints=[0,0,0,1],verbosity=-1,num_threads=2,seed=seed),lgb.Dataset(x,label=y),num_boost_round=120)
        pred=np.maximum(0,model.predict(grid).reshape(n,6))
        forecast=financial(pred,discounts,stock,price,cost,gamma)
        choice=forecast[3].argmax(axis=1)
        assert np.all(np.diff(pred,axis=1)>=-1e-8)
        assert np.all(forecast[0]<=stock[:,None]+1e-8)
        assert actual[3][row,choice].sum() <= actual[3][row,oracle_choice].sum()+1e-8
        records.append({'loss':'MSE' if loss=='regression' else 'Tweedie','seed':seed,'grid_rmse':float(np.sqrt(np.mean((pred-true)**2))),'forecast_profit_pct_oracle':float(100*forecast[2][row,choice].sum()/oracle_profit),'materialized_profit_pct_oracle':float(100*actual[2][row,choice].sum()/oracle_profit),'mean_discount':float(discounts[choice].mean())})
    return records


def main():
    records=[r for seed in (11,22,33) for r in experiment(seed)]
    discounts=np.arange(6)/10
    base=np.array([3.,8.,15.]); eps=np.array([2.,1.3,2.8])
    stock=np.array([40.,80.,100.]); price=np.array([100.,60.,80.])
    q=base[:,None]*3*(1-discounts)**(-eps[:,None])
    sales,nmv,profit,ltp=financial(q,discounts,stock,price,price*0.2,price*0.25)
    frames=[]
    for alpha in np.arange(0,2.01,0.1):
        choice=(ltp+alpha*nmv).argmax(axis=1); row=np.arange(3)
        frames.append({'alpha':round(float(alpha),1),'nmv':float(nmv[row,choice].sum()),'ltp':float(ltp[row,choice].sum()),'profit':float(profit[row,choice].sum()),'articles':[{'article':i+1,'discount':float(discounts[j]),'demand':float(q[i,j]),'stock':float(stock[i]),'sales':float(sales[i,j]),'nmv':float(nmv[i,j]),'ltp':float(ltp[i,j])} for i,j in enumerate(choice)]})
    assert all(frames[i+1]['nmv']>=frames[i]['nmv']-1e-8 for i in range(len(frames)-1))
    result={'lab05':'zalando','seeds':[11,22,33],'experiment':records,'frames':frames,'checks':{'discount_monotonicity':True,'stock_clip':True,'alpha_nmv_nondecreasing':True},'paper_evidence':{'source':'https://arxiv.org/pdf/2606.13741v1','table2':[{'model':'GBT','demand_error':0.574,'gmv_error':0.142,'rmse':3.24,'mape':0.052,'training_hours':7},{'model':'TSMixer','demand_error':0.614,'gmv_error':0.187,'rmse':3.12,'mape':0.042,'training_hours':18},{'model':'MLP','demand_error':0.612,'gmv_error':0.154,'rmse':3.02,'mape':0.040,'training_hours':24}],'table3':[{'model':'MSE','forecast':115.02,'materialized':93.07},{'model':'Tweedie','forecast':94.21,'materialized':91.57}],'table5':[{'metric':'PCII','effect':6.00,'low':0.79,'high':11.03},{'metric':'NMV','effect':2.23,'low':-0.83,'high':5.33},{'metric':'SIAR','effect':0.56,'low':-3.10,'high':4.26}]},'verification':{'mechanism':'CONFIRMED','performance':'NOT TESTED','scaling':'NOT TESTED','production_applicability':'NOT TESTED'}}
    Path(__file__).with_name('results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(records,indent=2))

if __name__=='__main__': main()
