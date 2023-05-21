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
uid='aaaaa'
usage_list = []
name_list = []
category_list=[]
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

usage_list = list(map(int, usage_list))
usage = sum(usage_list)
# usage_list = list(map(string, usage_list))

result = pd.DataFrame()

result['name'] = name_list
result['category'] = category_list
result['cost'] = usage_list

print(name_list)
print(category_list)
print(usage_list)

clist = ['금융' ,'미용&뷰티' ,'문구&디지털',  '통신',  '식비',  '의류&잡화',  '경조사',  '취미&여가',  '문화',  '교육',  '주거&생활',  '건강',  '교통']
Association_category_list = clist
Association_name_list = []
for v in name_list:
    if v not in Association_name_list:
        Association_name_list.append(v)
Association_name_list = list(set(name_list))
category = pd.DataFrame(index=Association_name_list, columns=Association_category_list)
category.fillna(0, inplace=True)
for i in range(len(Association_name_list)):
    my_category = result[result['name'] == Association_name_list[i]]['category'].values
    for j in range(len(my_category)):
        category.loc[Association_name_list[i]][my_category[j]] = category.loc[Association_name_list[i]][my_category[j]] + 1

print(category)




result.loc[result['name'] == uid, 'name'] = 1

ucategory = result['category'].mode()[0]

