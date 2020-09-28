from tkinter import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox
from tkinter import filedialog as fd
from datetime import datetime
from pandas import DataFrame
import sqlite3


def change_table(dif, data_to_use, number_tower):
    index = 0
    difference = dif
    arr_date = np.array([])
    arr_data = np.array([])
    while index < data_to_use['Date'].size:
        arr_date = np.append(arr_date, data_to_use.Date[index])
        average = 0
        for i in range(difference):
            if index >= data_to_use.Date.size:
                break
            average += data_to_use[number_tower][index]
            index += 1
        average /= difference
        arr_data = np.append(arr_data, average)
    dict_df = {'Date': arr_date, 'Data': arr_data}
    plt_df = pd.DataFrame(data=dict_df)
    plt_df[plt_df.Data >= 39].plot(x='Date', y='Data', rot=0, figsize=(14, 10), grid=True, label='Данные с утсановки')


def click_button_plt():
    if (magnitude.get() > 12) | (magnitude.get() < 1):
        messagebox.showinfo(message='Неверно введена бальность землетрясения')
        return
    if diff.get() < 1:
        messagebox.showinfo(message='Неверно введен шаг')
        return

    start_date, finish_date = '', ''
    try:
        start_date = datetime.strptime(date_with.get(), '%Y-%m-%d')
        finish_date = datetime.strptime(date_to.get() + ' 23:59', '%Y-%m-%d %H:%M')
    except ValueError:
        messagebox.showinfo(message='Неверно введена дата')
        return

    number_tower = 'Data_1st'
    if lang.get() == 1:
        number_tower = 'Data_1st'
    elif lang.get() == 2:
        number_tower = 'Data_2nd'
    elif lang.get() == 3:
        number_tower = 'Data_3rd'
    query1 = '''SELECT Date, %s FROM Data WHERE Date >= \'%s\' AND Date <= \'%s\';''' % (
        str(number_tower), start_date, finish_date)
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    try:
        out_df = pd.read_sql_query(query1, conn)
        out_df['Date'] = out_df['Date'].apply(pd.to_datetime)
        if h.get() == 1:
            if diff.get() == 1:
                out_df[out_df[number_tower] >= 39].plot(x='Date', y=number_tower, rot=0,
                                                        xlim=(out_df.Date[0], out_df.Date[out_df.Date.size - 1]),
                                                        figsize=(14, 10), grid=True, label='Данные с установки')
            else:
                change_table(diff.get(), out_df, number_tower)
        elif h.get() == 0:
            delta = finish_date - start_date
            if (int(delta.days) > 7) & (int(delta.days) <= 30):
                change_table(6, out_df, number_tower)
            elif (int(delta.days) >= 31) & (int(delta.days) <= 365):
                change_table(12, out_df, number_tower)
            elif int(delta.days) > 365:
                change_table(24, out_df, number_tower)
            else:
                out_df[out_df[number_tower] >= 39].plot(x='Date', y=number_tower, rot=0,
                                                        figsize=(14, 10), grid=True, label='Данные с установки')
        query2 = '''SELECT * FROM earthquake WHERE Time >= \'%s\' AND Time <= \'%s\' AND Magnitude >= %s;''' \
                 % (start_date, finish_date, magnitude.get())
        earthquake_df = pd.read_sql_query(query2, conn)
        earthquake_df['Time'] = earthquake_df['Time'].apply(pd.to_datetime)

        ax = plt.gca()
        ccol = np.array(earthquake_df.Magnitude)
        earthquake_df['Magnitude'] = earthquake_df['Magnitude'].apply(lambda x: x * 10)
        colormap = 'autumn'
        sctr = ax.scatter(x=list(earthquake_df.Time), y=list(earthquake_df.Magnitude), marker='o',
                          cmap=colormap, c=ccol, label='Землетрясения')
        if shc.get() == 1:
            plt.colorbar(sctr, ax=ax, format='%g', pad=0.03, aspect=30)

        plt.show()
    except (TypeError):
        messagebox.showinfo(message='Нет данных за этот период')
    finally:
        conn.close()


def click_button_path():
    file_name = fd.askopenfilename()
    path.set(file_name)


def click_button_addBD():
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    file_path = u'%s' % path.get()
    file = conn
    try:
        file = open(file_path)

        if BD.get() == 1:
            try:
                Data = pd.read_csv(file, sep='\s+', header=None,
                                   names=['Date', 'Time', 'Data_1st', 'Data_2nd', 'Data_3rd'],
                                   parse_dates=['Date'], encoding='utf8')

                arrDate = np.array([])
                for i in range(Data['Date'].size):
                    hour = datetime.strptime(str(Data['Date'][i].day) + '-' + str(Data['Date'][i].month) + '-'
                                             + str(Data['Date'][i].year) + ' ' + str(Data['Time'][i]), '%d-%m-%Y %H')
                    arrDate = np.append(arrDate, values=[hour])

                arrData_1 = np.array(Data.Data_1st)
                arrData_2 = np.array(Data.Data_2nd)
                arrData_3 = np.array(Data.Data_3rd)
                dict_of_data = {'Date': arrDate, 'Data_1st': arrData_1, 'Data_2nd': arrData_2, 'Data_3rd': arrData_3}
                data_to_use: DataFrame = pd.DataFrame(data=dict_of_data)
                data_to_use.index = data_to_use['Date']
                del data_to_use['Date']
                conn.commit()
                for i in range(data_to_use.index.size):
                    upsert = '''INSERT OR REPLACE INTO Data (Date, Data_1st, Data_2nd, Data_3rd) VALUES (\'%s\', %s, %s, %s)''' \
                             % (data_to_use.index[i], data_to_use.Data_1st[i], data_to_use.Data_2nd[i],
                                data_to_use.Data_3rd[i])
                    cursor.execute(upsert)
                conn.commit()
            except:
                messagebox.showinfo(message='Неверный формат для БД(LVD)')

        elif BD.get() == 2:
            try:
                df = pd.read_csv(file, sep='|')
                df['Time'] = df['Time'].apply(pd.to_datetime)
                # df['Magnitude'] = df['Magnitude'].apply(int)
                dict_of_data = {'Time': df['Time'], 'Magnitude': df['Magnitude']}
                data_to_use = pd.DataFrame(data=dict_of_data)
                data_to_use.index = data_to_use['Time']
                del data_to_use['Time']
                conn.commit()
                for i in range(data_to_use.index.size):
                    upsert = '''INSERT OR REPLACE INTO earthquake (Time, Magnitude) VALUES (\'%s\', %s)''' \
                             % (data_to_use.index[i], data_to_use.Magnitude[i])
                    cursor.execute(upsert)
                conn.commit()
            except:
                messagebox.showinfo(message='Неверный формат для БД(землетрясения)')

    except FileNotFoundError:
        messagebox.showinfo(message='Не выбран файл')
    except IOError:
        messagebox.showinfo(message='Невозможно открыть файл')
    finally:
        file.close()

    conn.close()


def click_button_day_week():
    try:
        day = datetime.strptime(date_week.get(), '%Y-%m-%d')
        day = datetime.weekday(day)
        if day == 0:
            day_week.set('Понедельник')
        elif day == 1:
            day_week.set('Вторник')
        elif day == 2:
            day_week.set('Среда')
        elif day == 3:
            day_week.set('Четверг')
        elif day == 4:
            day_week.set('Пятница')
        elif day == 5:
            day_week.set('Суббота')
        elif day == 6:
            day_week.set('Воскресенье')
    except ValueError:
        messagebox.showinfo(message='Неверно введена дата')


root = Tk()
root.title("LVD")
root.geometry("800x550+250+50")
color = 'grey'
root.configure(background=color)

header = Label(text='Выберите номер башни', background=color)
header.place(relx=.009, rely=.05, height=20, width=150, bordermode=OUTSIDE)
lang = IntVar()
lang.set(1)
first_tower = Radiobutton(text='Первая', value=1, variable=lang, background=color)
first_tower.place(relx=.3, y=15, height=25, relwidth=.2, bordermode=INSIDE)

second_tower = Radiobutton(text='Вторая', value=2, variable=lang, background=color)
second_tower.place(relx=.45, y=15, height=25, relwidth=.2, bordermode=INSIDE)

third_tower = Radiobutton(text='Третья', value=3, variable=lang, background=color)
third_tower.place(relx=.6, y=15, height=25, relwidth=.2, bordermode=INSIDE)

#########

path = StringVar()
path_entry = Entry(textvariable=path)
path_entry.place(relx=.05, rely=.59, height=25, relwidth=.4, bordermode=INSIDE)

path_btn = Button(text="Выбрать", background="#555", foreground="#ccc",
                  padx="20", pady="8", font="16", command=click_button_path)
path_btn.place(relx=.6, rely=.59, relheight=.1, relwidth=.2, bordermode=INSIDE)

path_btn = Button(text="Добавить в БД", background="#555", foreground="#ccc",
                  padx="20", pady="8", font="16", command=click_button_addBD)
path_btn.place(relx=.6, rely=.69, relheight=.1, relwidth=.3, bordermode=INSIDE)

BD = IntVar()
BD.set(1)
LVD_bd = Radiobutton(text='БД (LVD)', value=1, variable=BD, background=color)
LVD_bd.place(relx=.05, rely=.69, height=15, relwidth=.11, bordermode=INSIDE)
earthquake_bd = Radiobutton(text='БД (землетрясения)', value=2, variable=BD, background=color)
earthquake_bd.place(relx=.19, rely=.69, height=15, relwidth=.22, bordermode=INSIDE)
############

header_with = Label(text='С (гггг-мм-дд)', background=color)
header_with.place(relx=.05, rely=.18, height=20, width=90, bordermode=OUTSIDE)
date_with = StringVar()
date_with.set('2009-01-01')
date_with_entry = Entry(textvariable=date_with)
date_with_entry.place(relx=.05, rely=.23, height=25, relwidth=.2, bordermode=INSIDE)

header_to = Label(text='До (гггг-мм-дд)', background=color)
header_to.place(relx=.3, rely=.18, height=20, width=90, bordermode=OUTSIDE)
date_to = StringVar()
date_to.set('2009-12-31')
date_to_entry = Entry(textvariable=date_to)
date_to_entry.place(relx=.3, rely=.23, height=25, relwidth=.2, bordermode=INSIDE)
##########

header_with = Label(text='Шаг между точками в часах', background=color)
header_with.place(relx=.02, rely=.35, height=20, width=155, bordermode=OUTSIDE)
diff = IntVar()
diff.set(1)
date_with_entry = Entry(textvariable=diff)
date_with_entry.place(relx=.22, rely=.35, height=20, width=60, bordermode=INSIDE)

h = IntVar()
step_checkbutton = Checkbutton(text="Выбрать свой шаг", variable=h, bg=color, onvalue=1, offvalue=0)
step_checkbutton.pack()
step_checkbutton.place(relx=.02, rely=.42, bordermode=INSIDE)

header_to = Label(text='Бальность землетрясения', background=color)
header_to.place(relx=.32, rely=.35, height=20, width=150, bordermode=OUTSIDE)
magnitude = IntVar()
magnitude.set(4)
date_to_entry = Entry(textvariable=magnitude)
date_to_entry.place(relx=.51, rely=.35, height=20, width=35, bordermode=INSIDE)

shc = IntVar()
step_checkbutton = Checkbutton(text="Вкл шкалу землетрясений", variable=shc, bg=color, onvalue=1, offvalue=0)
step_checkbutton.pack()
step_checkbutton.place(relx=.33, rely=.42, bordermode=INSIDE)

plt_btn = Button(text='Построить график', background='green', foreground='#ccc',
                 padx='20', pady='8', font='16', command=click_button_plt)
plt_btn.place(relx=.05, rely=.9, relheight=.1, relwidth=.9, bordermode=INSIDE)

date_week = StringVar()
date_week.set('Дата (гггг-мм-дд)')
date_week_entry = Entry(textvariable=date_week)
date_week_entry.place(relx=.7, rely=.23, height=25, relwidth=.2, bordermode=INSIDE)

image = PhotoImage(file='image_2.png')
week_btn = Button(image=image, background='grey', foreground='#ccc',
                  padx='20', pady='8', font='8', command=click_button_day_week)
week_btn.place(relx=.77, rely=.29, height=50, width=45, bordermode=OUTSIDE)

day_week = StringVar()
day_week.set('День недели')
day_week_entry = Entry(textvariable=day_week)
day_week_entry.place(relx=.7, rely=.4, height=25, relwidth=.2, bordermode=INSIDE)

root.mainloop()
