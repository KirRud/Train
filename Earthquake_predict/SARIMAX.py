import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import sqlite3
import statsmodels.api as sm
from statsmodels.iolib.table import SimpleTable
import warnings

start_date = datetime.strptime("2009-01-01", "%Y-%m-%d")
finish_date = datetime.strptime("2009-12-31 23:59", "%Y-%m-%d %H:%M")
number_tower = "Data_1st"

query = '''SELECT Date, %s FROM Data WHERE  Date >=  \'%s\' AND Date <= \'%s\';''' % (
    str(number_tower), start_date, finish_date)
conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
dataset = pd.read_sql_query(query, conn)
dataset.Date = dataset['Date'].apply(pd.to_datetime)
dataset.index = dataset.Date
dataset.drop('Date', axis='columns', inplace=True)
dataset.replace(0, dataset.mean(), inplace=True)

res = dataset.describe()
dataset.hist()
print(res)
V = res.Data_1st["std"] / res.Data_1st["mean"]
print(f"V = {V}")

row = ['JB', 'p-value', 'skew', 'kurtosis']
jb_test = sm.stats.stattools.jarque_bera(dataset)
a = np.vstack([jb_test])
res = SimpleTable(a, row)
print(res)
test = sm.tsa.adfuller(dataset.Data_1st)
print(test)
print('adf: ', test[0])
print('p-value: ', test[1])
print('Critical values: ', test[4])
if test[0] > test[4]['5%']:
    print('Есть единичные корни, ряд не стационарен')
else:
    print('Единичных корней нет, ряд стационарен')

warnings.filterwarnings("ignore")  # отключает предупреждения
src_data_model = dataset[:"2009-08-31"]
model = sm.tsa.statespace.SARIMAX(src_data_model,
                                  order=(1, 1, 1),
                                  seasonal_order=(1, 1, 1, 12),
                                  enforce_stationarity=False,
                                  enforce_invertibility=False)
res = model.fit()
# res.plot_diagnostics(figsize=(15, 12))

pred = res.predict(pd.to_datetime('2009-01-01'), pd.to_datetime('2009-12-31'), dynamic=False)
pred = pd.DataFrame(pred)
dataset.plot(figsize=(12, 6))
ax = plt.gca()
pred.plot(ax=ax)
plt.show()
conn.close()
