import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.ndimage.interpolation import shift

gl_start_date = datetime.strptime("2009-01-01", "%Y-%m-%d")
gl_finish_date = datetime.strptime("2016-12-31 23:59", "%Y-%m-%d %H:%M")


def X_day(dataset, start_date=gl_start_date, finish_date=gl_finish_date):
    X = np.array(dataset[f'{start_date.date()}'])
    X = X.transpose()
    for date in pd.date_range(start_date + timedelta(days=1), finish_date):
        buff_X = np.array(dataset[f'{date.date()}'])
        try:
            X = np.vstack((X, buff_X.transpose()))
        except:
            mean = buff_X.mean()
            ch_tdelta = timedelta(hours=23)
            correct_array = list()
            for check_hour in pd.date_range(date, date + ch_tdelta, freq='H').strftime('%Y-%m-%d %H:%M:%s').tolist():
                if str(check_hour) in dataset.index:
                    correct_array.append(dataset.loc[f'{check_hour}'][0])
                else:
                    correct_array.append(mean)
            correct_array = np.array([correct_array])
            X = np.vstack((X, correct_array))
    return X


def y_day(earthquake_df, start_date=gl_start_date, finish_date=gl_finish_date):
    y = list()
    for date in pd.date_range(start_date, finish_date):
        flg = earthquake_df.index.str.find(str(date.date()))
        if 0 in flg:
            y.append(1)
        else:
            y.append(0)

    y = np.array(y)
    y = shift(y, -2, cval=0)
    return y


def one_day(dataset, earthquake_df, start_date=gl_start_date, finish_date=gl_finish_date):
    X = X_day(dataset, start_date, finish_date)
    y = y_day(earthquake_df, start_date, finish_date)
    return X, y


def X_week(dataset, start_date=gl_start_date, finish_date=gl_finish_date):
    X = np.array(dataset[f'{start_date.date()}'])
    X = X.transpose()
    for date in pd.date_range(start_date + timedelta(days=1), finish_date):
        buff_X = np.array(dataset[f'{date.date()}'])
        # date_list.append(date)
        try:
            X = np.vstack((X, buff_X.transpose()))
        except:
            mean = buff_X.mean()
            ch_tdelta = timedelta(hours=23)
            correct_array = list()
            for check_hour in pd.date_range(date, date + ch_tdelta, freq='H').strftime('%Y-%m-%d %H:%M:%s').tolist():
                if str(check_hour) in dataset.index:
                    correct_array.append(dataset.loc[f'{check_hour}'][0])
                else:
                    correct_array.append(mean)
            correct_array = np.array([correct_array])
            X = np.vstack((X, correct_array))
    count = 0
    for str_X in X:
        if count == 7 or count == 0:
            buff_X = str_X
            count = 1
            continue
        buff_X = np.hstack([buff_X, str_X])
        count += 1
        if count == 7:
            try:
                X = np.vstack([X, buff_X])
            except:
                X = buff_X
    return X


def y_week(earthquake_df, start_date=gl_start_date, finish_date=gl_finish_date):
    y = list()
    for gl_date in pd.date_range(start_date, finish_date, freq='W'):
        count = 0
        for date in pd.date_range(gl_date, gl_date + timedelta(days=6)):
            # print(date)
            flg = earthquake_df.index.str.find(str(date.date()))
            if 0 in flg:
                y.append(1)
                break
            else:
                count += 1
            if count == 7:
                y.append(0)

    y = np.array(y)
    y = shift(y, -2, cval=0)
    return y


def one_week(dataset, earthquake_df, start_date=gl_start_date, finish_date=gl_finish_date):
    X = X_week(dataset, start_date, finish_date)
    y = y_week(earthquake_df, start_date, finish_date)
    return X, y
