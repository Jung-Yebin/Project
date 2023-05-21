import pyrebase
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
import calendar
import seaborn as sns
import numpy as np
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras import models
from keras.engine.functional import Functional
import tensorflow


firebaseConfig = {
            "apiKey": "AIzaSyBFIpc30kRLllfUs710cbbGZTasFXEYXPk",
            "authDomain": "vita-d7ca1.firebaseapp.com",
            "databaseURL": "https://vita-d7ca1-default-rtdb.firebaseio.com",
            "projectId": "vita-d7ca1",
            "storageBucket": "vita-d7ca1.appspot.com",
            "messagingSenderId": "860961095524",
            "appId": "1:860961095524:web:fdddb042dab3b2d7fec471",
            "measurementId": "G-MRS6WFXE9C"
        }
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

date_list = [] ##추가
usage_list = []
category_list=[]

uid = "aaaaa"


date_list = []
usage_list = []
name_list = []
category_list=[]
date = db.child("Calendar").child(uid).get()

for k, v in date.val().items():

    for i in range(len(db.child("Calendar").child(uid).child().get().val())):
        category = db.child("Calendar").child(uid).child(k).get()

    for k2, v2 in category.val().items():
        if None in v2 and len(v2) == 2:
            v2 = {'1': v2[-1]}

        for j in range(len(db.child("Calendar").child(uid).child(k).child().get().val())):
            num = v2

        for k3, v3 in num.items():
            for n in range(len(k3)):
                cost = v3
                for k4, v4 in cost.items():
                    date_list.append(k)
                    usage_list.append(v4)
                    name_list.append(uid)
                    category_list.append(k2)
# 사용자의 목표 소비 예산
users = db.child("User").get().val()
for k, v in users.items():
    if k == uid:
        for k_budget, v_budget in v.items():
            if k_budget == 'budget':
                users_budget = v_budget

usage_list = list(map(int, usage_list))
today = datetime.today()
thisyear = today.strftime("%Y")

result = pd.DataFrame()
result['name'] = name_list
result['date'] = date_list
result['category'] = category_list
result['cost'] = usage_list

print(name_list)
print(date_list)
print(category_list)
print(usage_list)

dataFilter = result['date'].str.contains(thisyear)
result = result[dataFilter]

## 사용자가 올해 소비한 총 금액
#usage_list = result['cost'].to_list()
#usage = sum(usage_list)

## 사용자가 이번달 소비한 총 금액
#thismonth = today.strftime("%Y-%m")
#dataFilter = result['date'].str.contains(thismonth)
#uthismonth = result[dataFilter]
#uthismonth = uthismonth['cost'].to_list()
#uthismonth = list(map(int, uthismonth))
#uthismonth = sum(uthismonth)

## 사용자가 올해 소비한 총 금액
#uthisyear = result['cost'].to_list()
#uthisyear = list(map(int, uthisyear))
#uthisyear = sum(uthisyear)

## 다음달 예측 소비금액
#result.loc[result['name'] == uid, 'name'] = 1

#ucategory = result['category'].mode()[0]

#x = result[['name']]
#y = result[['cost']]

#min_test_size = 2

#if len(result) >= min_test_size:
#    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=10)
#    model = LinearRegression()
#    model.fit(x_train, y_train)
#    y_predict = model.predict(x_test)

#    mse = mean_squared_error(y_test, y_predict)
#    mse ** 0.5
#    y_predict = y_predict[0]

#else :
#    y_predict = 0

price = result['cost']

seq_len = 0
window_size = seq_len + 1

values = []
for i in range(len(price) - seq_len):
    values.append(price[i:i+seq_len])

#데이터 정규화
nomalized_data = []
for i in values:
    nomalized_window = [((float(k) / float(i[0])) - 1 for k in i)]
    nomalized_data.append(nomalized_window)

values = np.array(nomalized_data)

print(int(round(values.shape[0] * 0.9)))

row = int(round(values.shape[0] * 0.9))
train = values[:row, :]
np.random.shuffle(train)

x_train = train[:, :-1]
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
y_train = train[:, -1]
x_test = values[row:, :-1]
x_test = np.reshape(x_test,(x_test.shape[0], x_test.shape[1], 1))
y_test = values[row:, -1]

print(result)

print(x_train.shape)
print(x_test.shape)

print()
print(result['name'])
print(result['date'])
print(result['category'])
print(result['cost'])
print()

print(price)