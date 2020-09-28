from keras.utils import to_categorical
from keras.layers.core import Dense
from keras.layers import Activation
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
from sklearn.model_selection import train_test_split
from keras.layers import Input, Dropout
from keras import Model
from sklearn.metrics import classification_report
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM
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
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=1)

num_classes = 2
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)
max_features = X_train.shape[0]
maxlen = X_train.shape[1]
batch_size = 5

a = Input(shape=(X_train.shape[1],))
b = Embedding(max_features, 512, input_length=maxlen)(a)
b = LSTM(64, return_sequences=True)(b)
b = LSTM(64)(b)
b = Dropout(.5)(b)
b = Dense(2)(b)
b = Activation('softmax')(b)
model = Model(inputs=a, outputs=b)

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

epochs = 1
history = model.fit(X_train, y_train,
                    batch_size=batch_size,
                    epochs=epochs,
                    verbose=1,
                    validation_split=0.1)
score = model.evaluate(X_test, y_test, batch_size=batch_size)
print("Test-Accuracy:", np.mean(history.history["val_acc"]))
predict = np.round(model.predict(X_test))
print('RNN:\n', classification_report(y_test, predict, digits=5))
# # Генерируем описание модели в формате yaml
# model_yaml = model.to_yaml()
# yaml_file = open("model_week.yml", "w")
# # Записываем модель в файл
# yaml_file.write(model_yaml)
# yaml_file.close()
# model.save_weights("model_week.h5")
