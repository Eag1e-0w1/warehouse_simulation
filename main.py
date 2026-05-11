from math import ceil
import pandas as pd
from models import load_warehouse_params
from config import PATH
from simulator import Warehouse
from calculator import Calculator

sim = Warehouse()
calc = Calculator()
params = load_warehouse_params(PATH)

scenarios = {
    'no_amr': params.model_copy(update={'amr_num': 0,
                                     'productivity': 1,
                                     'pickers': 40}),
    'amr': params.model_copy(update={'amr_num': 100,
                                     'productivity': 1.4,
                                     'pickers': 26})
}

metrics = {}
for name, param in scenarios.items():
    data = sim.run(param)
    result = calc.calculate(param, data)
    metrics[name] = {'params': param, 'result': result, 'data': data}


df = pd.DataFrame(index=[key for key in metrics['no_amr']['result'].keys()],
                 data={'no_amr':[value for value in metrics['no_amr']['result'].values()],
                       'amr':[value for value in metrics['amr']['result'].values()]})

for col in df.columns:
    df[col] = round(df[col],1)

df['effect'] = df['amr'] - df['no_amr']
min_monthly_profit = ceil(calc.compute_min_monthly_profit(df))

print(df)
print(min_monthly_profit)