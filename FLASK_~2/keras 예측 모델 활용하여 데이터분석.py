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
from tensorflow.python.keras.layers import LSTM, Dense


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

        my = {}
        if None in v2 and len(v2) > 2:
            for i, v in enumerate(v2[1:], start=1):
                my[str(i)] = v
            v2 = my


        for v3 in v2.values():
            usage_list += v3.values()
            name_list.append(uid)
            date_list.append(k)
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

print(name_list)
print(date_list)
print(category_list)
print(usage_list)
result = pd.DataFrame()
result['name'] = name_list
result['date'] = date_list
result['category'] = category_list
result['cost'] = usage_list

#dataFilter = result['date'].str.contains(thisyear)
#result = result[dataFilter]

price = list(result['cost'])
price = np.array(price)

seq_len = 10
window_size = seq_len + 1

values = []
for i in range(len(price) - seq_len):
    values.append(price[i:i+seq_len])

#데이터 정규화
nomalized_data = []
for i in values:
    nomalized_window = [((float(k) / float(i[0])) - 1) for k in i]
    nomalized_data.append(nomalized_window)

values = np.array(nomalized_data)

row = int(round(values.shape[0] * 0.8))
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


#모델 생성
model = Sequential()

model.add(LSTM(9, return_sequences=True, input_shape=(9,1)))
model.add(LSTM(32, return_sequences=False))
model.add(Dense(1,activation='linear'))
model.compile(loss='mse', optimizer='rmsprop', metrics=['accuracy'])

#트레이닝
history = model.fit(x_train, y_train,validation_data=(x_test, y_test), batch_size=10, epochs=10)

#예측
pred = model.predict(x_test)

#fig = plt.figure(facecolor='white')
#ax = fig.add_subplot(111)
#ax.plot(y_test, label='data')
#ax.plot(pred, label='preidction')
#ax.legend()
#plt.show()


# 학습 정확성 값과 검증 정확성 값을 플롯팅 합니다.
print(history.history)
plt.plot(history.history['accuracy'])
plt.plot(history.history['loss'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['accuracy', 'Loss'], loc='upper left')
#plt.savefig('tran_result.png')
plt.show()

print(pred[0])

#역정규화
min_value = result['cost'].min()
max_value = result['cost'].max()

v = np.array(pred[0])
prediction = v[0]
prediction = (prediction * (max_value - min_value)) + min_value

print(prediction)