import pandas as pd
import numpy as np
# import mglearn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pandas import DataFrame
import sqlite3
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from scipy.ndimage.interpolation import shift
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_curve, classification_report
from sklearn.metrics import classification_report, roc_curve
import seaborn as sns

start_date = datetime.strptime("2009-01-01", "%Y-%m-%d")
finish_date = datetime.strptime("2011-12-31 23:59", "%Y-%m-%d %H:%M")
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
# earthquake_df['Time'] = earthquake_df['Time'].apply(pd.to_datetime)
earthquake_df.index = earthquake_df.Time
earthquake_df.drop('Time', axis='columns', inplace=True)

buff_X = np.array(dataset[f'{start_date.date()}'])
buff_X = buff_X.transpose()
date_list = list()
count = 1
X = np.array(list())

for date in pd.date_range(start_date + timedelta(days=1), finish_date):

    if count < 7:
        buff_arr = np.array(dataset[f'{date.date()}'])
        if buff_X.shape[0] == 0:
            buff_X = np.array(buff_arr.transpose())
        else:
            buff_X = np.vstack((buff_X, buff_arr.transpose()))

        count += 1
    if count == 7:
        count = 0
        date_list.append(date.date() - timedelta(days=6))
        if X.shape[0] == 0:
            X = np.array(buff_X.ravel())
        else:
            X = np.vstack((X, buff_X.ravel()))
        buff_X = np.array(list())
if buff_X.shape[0] != 0:
    # zer = np.zeros((1, X.shape[1] - buff_X.ravel().shape[0]))
    buff_X = np.append(buff_X, np.zeros((1, X.shape[1] - buff_X.ravel().shape[0])))
    X = np.vstack((X, buff_X))

y = list()
count = 0
seism = False
for date in pd.date_range(start_date, finish_date):
    count += 1
    flg = earthquake_df.index.str.find(str(date.date()))
    if 0 in flg:
        seism = True
    if count == 7:
        count = 0
        if seism:
            y.append(1)
        else:
            y.append(0)
        seism = False
if count != 0:
    if seism:
        y.append(1)
    else:
        y.append(0)

y = np.array(y)
y = shift(y, -2, cval=0)  # shift for n week(2 in this moment)

param_grid = {'C': [0.001, 0.01, 0.1, 1, 10, 100],
              'gamma': [0.001, 0.01, 0.1, 1, 10, 100]}
grid_search = GridSearchCV(SVC(), param_grid, cv=5)

# if 1 in y:
#     print(len(y))
#     print(y)
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=0)
grid_search.fit(X_train, y_train)

forest = RandomForestClassifier(n_estimators=1, random_state=4, n_jobs=6, max_depth=3)
forest.fit(X_train, y_train)

gbrt = GradientBoostingClassifier(random_state=2, max_depth=1, learning_rate=1)
gbrt.fit(X_train, y_train)

#metrics
print('Правильность на обуч наборе: {:.3f}'.format(gbrt.score(X_train, y_train)))
print('Правильность на тестовом наборе: {:.3f}'.format(gbrt.score(X_test, y_test)))

# print(forest)
print('Правильность на обуч наборе: {:.3f}'.format(forest.score(X_train, y_train)))
print('Правильность на тестовом наборе: {:.3f}'.format(forest.score(X_test, y_test)))
# confusion = confusion_matrix(y_test, forest.predict(X_test)) #матрица ошибок
print(classification_report(y_test, forest.predict(X_test), target_names=["earthquake", "none earthquake"]))
print(classification_report(y_test, gbrt.predict(X_test)))

precision_rf, recall_rf, thresholds_rf = precision_recall_curve(y_test, forest.predict_proba(X_test)[:, 1])
precision_gbrt, recall_gbrt, thresholds_gbrt = precision_recall_curve(y_test, gbrt.decision_function(X_test))

plt.plot(precision_rf, recall_rf, label='RF')
plt.plot(precision_gbrt, recall_gbrt, label='GBRT')
plt.xlabel("Precision")
plt.ylabel('Recall')
plt.legend('best')
plt.legend(loc=2)
plt.show()

fpr_rf, tpr_rf, thresholds_rf = roc_curve(y_test, forest.predict_proba(X_test)[:, 1])
fpr_gbrt, tpr_gbrt, thresholds_gbrt = roc_curve(y_test, gbrt.decision_function(X_test))
plt.plot(fpr_rf, tpr_rf, label='ROC RF')
plt.plot(fpr_gbrt, tpr_gbrt, label='ROC GBRT')
plt.xlabel('FPR')
plt.ylabel('TPR')
plt.legend(loc=4)
plt.show()
