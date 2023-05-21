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


date = db.child("Calendar").child(uid).get()
for k, v in date.val().items():

    for i in range(len(db.child("Calendar").child(uid).child().get().val())):
        category = db.child("Calendar").child(uid).child(k).get()

    for k2, v2 in category.val().items():
        if None in v2:
                    v2 = {'1': v2[-1]}

        for j in range(len(db.child("Calendar").child(uid).child(k).child().get().val())):
            num = v2

        for k3, v3 in num.items():

            for n in range(len(k3)):
                cost = v3

                for k4, v4 in cost.items():
                    date_list.append(k) ##추가
                    usage_list.append(v4)
                    category_list.append(k2)

users = db.child("User").get().val()
for k, v in users.items():
        if k == uid:
            for k_budget, v_budget in v.items():
                if k_budget == 'budget':
                    users_budget = v_budget

print(users_budget)

usage_list = list(map(int, usage_list))

today = datetime.today()
thisyear = today.strftime("%Y")

df = pd.DataFrame()
df['date'] = date_list
df['usage'] = usage_list


dataFilter = df['date'].str.contains(thisyear)
df = df[dataFilter]

print(df)

usage = sum(usage_list)