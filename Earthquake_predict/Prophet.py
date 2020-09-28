import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import sqlite3
import warnings
from fbprophet import Prophet
warnings.filterwarnings("ignore")

start_date = datetime.strptime("2009-01-01", "%Y-%m-%d")
finish_date = datetime.strptime("2011-12-31 23:59", "%Y-%m-%d %H:%M")
number_tower = "Data_1st"

query = '''SELECT Date, %s FROM Data WHERE  Date >=  \'%s\' AND Date <= \'%s\';''' % (
    str(number_tower), start_date, finish_date)
conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
dataset = pd.read_sql_query(query, conn)
dataset.Date = dataset["Date"].apply(pd.to_datetime)

print(dataset)

predictions = 180
# приводим dataframe к нужному формату
df = dataset
print(df.head())
df.columns = ['ds', 'y']
# отрезаем из обучающей выборки последние 30 точек, чтобы измерить на них качество
train_df = df[:-predictions]

m = Prophet()
m.fit(train_df)

future = m.make_future_dataframe(periods=predictions)
forecast = m.predict(future)

m.plot(forecast)
m.plot_components(forecast)

plt.show()
