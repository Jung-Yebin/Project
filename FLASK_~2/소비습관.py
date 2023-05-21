import pyrebase
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime

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

uid = "ababab"


usage_list = []
name_list = []
date_list = []
category_list = []
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
                    usage_list.append(v4)
                    name_list.append(uid)
                    category_list.append(k2)
                    date_list.append(k)

usage_list = list(map(int, usage_list))
usage = sum(usage_list)
# usage_list = list(map(string, usage_list))

result = pd.DataFrame()

result['date'] = date_list
result['name'] = name_list
result['category'] = category_list
result['cost'] = usage_list

print(result)

#print(date_list)

time = datetime.today().strftime("%Y-%m")
#print(time)


monthdate_list=[]

for i in range(len(date_list)):
    if time in date_list[i]:
        monthdate_list.append(date_list[i])

monthdate_list = list(set(monthdate_list))
print(monthdate_list)

print(len(monthdate_list))

month_usage = []

for i in range(len(monthdate_list)):
    month_category = db.child("Calendar").child(uid).child(monthdate_list[i]).get().val()
    for k, v in month_category.items():

        if None in v:
            v = {'1': v[-1]}

        for j in range(len(db.child("Calendar").child(uid).child(monthdate_list[i]).child().get().val())):
            num = v

        for k2, v2 in num.items():

            for n in range(len(k2)):
                cost = v2

                for k3, v3 in cost.items():
                    month_usage.append(v3)


df = pd.DataFrame()
df['mcost'] = month_usage
print(df)

month_freq = round(30 / len(monthdate_list))
month_usage = list(map(int, month_usage))
month_usage = sum(month_usage)
month_usage2 = round(month_usage / len(monthdate_list))



print(month_usage2)
print(month_freq)
