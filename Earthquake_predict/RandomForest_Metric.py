import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, f1_score
import warnings
import change_data as cd

warnings.simplefilter('ignore')

start_date = datetime.strptime("2009-01-01", "%Y-%m-%d")
finish_date = datetime.strptime("2016-12-31 23:59", "%Y-%m-%d %H:%M")
number_tower = "Data_1st"

query = '''SELECT Date, %s FROM Data WHERE  Date >=  \'%s\' AND Date <= \'%s\';''' % (
    str(number_tower), start_date, finish_date)
conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
dataset = pd.read_sql_query(query, conn)
dataset.Date = dataset['Date'].apply(pd.to_datetime)
dataset.index = dataset.Date
dataset.drop('Date', axis='columns', inplace=True)

magnitude = 4
query2 = '''SELECT * FROM earthquake WHERE Time >= \'%s\' AND Time <= \'%s\' AND Magnitude >= %s;''' \
         % (start_date, finish_date, magnitude)
earthquake_df = pd.read_sql_query(query2, conn)
earthquake_df.index = earthquake_df.Time
earthquake_df.drop('Time', axis='columns', inplace=True)

try:
    choice_time = int(input('За день(0) или за неделю(1)? \n'))
except:
    choice_time = 0
if choice_time == 0:
    X, y = cd.one_day(dataset, earthquake_df)
elif choice_time == 1:
    X, y = cd.one_week(dataset, earthquake_df)
else:
    X, y = cd.one_week(dataset, earthquake_df)

params_rf = {
    'n_estimators': range(1, 10),
    'random_state': [1, 2, 4, 8, 16, 32, 42, 64],
    'n_jobs': [6],
    'max_depth': range(1, 10),
}
params_gbrt = {
    'n_estimators': range(1, 10),
    'random_state': [1, 2, 4, 8, 16, 32, 42, 64],
    'max_depth': range(1, 10),
    'learning_rate': np.linspace(.1, 1, 10),
}

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)
forest = RandomForestClassifier(n_estimators=3, random_state=32, n_jobs=6, max_depth=8)
forest.fit(X_train, y_train)

gbrt = GradientBoostingClassifier(random_state=2, max_depth=7, learning_rate=.2, n_estimators=8)
gbrt.fit(X_train, y_train)
print('Правильность на обуч наборе: {:.3f}'.format(gbrt.score(X_train, y_train)))
print('Правильность на тестовом наборе: {:.3f}'.format(gbrt.score(X_test, y_test)))

# print(forest)
print('Правильность на обуч наборе: {:.3f}'.format(forest.score(X_train, y_train)))
print('Правильность на тестовом наборе: {:.3f}'.format(forest.score(X_test, y_test)))

print('Случайный лес:\n',
      classification_report(y_test, forest.predict(X_test), target_names=["none earthquake", "earthquake"]))
print('Градиентный бустинг:\n',
      classification_report(y_test, gbrt.predict(X_test), target_names=["none earthquake", "earthquake"]))

print('Случайный лес:\n',
      f1_score(y_test, forest.predict(X_test)))
print('GRBT:\n',
      f1_score(y_test, gbrt.predict(X_test)))

# rand_forest = GridSearchCV(forest, params_rf, 'f1_weighted', n_jobs=6)
# rand_forest.fit(X_train, y_train)
# params = rand_forest.best_params_
# print(params)
#
# gbrt_forest = GridSearchCV(gbrt, params_gbrt, 'f1_weighted', n_jobs=6)
# gbrt_forest.fit(X_train, y_train)
# params = gbrt_forest.best_params_
# print(params)
