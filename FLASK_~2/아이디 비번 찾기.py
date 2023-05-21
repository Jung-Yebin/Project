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

users = db.child("User").get().val()
key1 = '비타민'
key2 = '010-1234-5678'

print(users)

name_val = []
number_val = []
for k, v in users.items():
    print(k)
    print(v)
    for k2,v2 in v.items():
        if v2 == key1:
            name_val.append(k)

    for k3, v3 in v.items():
        if v3 == key2:
            number_val.append(k)

result = []
for i in set(name_val):
    for j in set(number_val):
        if i == j:
            result.append(i)

if len(result) != 0:
    key = result.pop()

    user_id = ''
    for k, v in users.items():
        if k == key:
            for id_k,id_v in v.items():
                if id_k == 'id':
                    user_id = id_v
    user_pwd = ''
    for k, v in users.items():
        if k == key:
            for pwd_k,pwd_v in v.items():
                if pwd_k == 'pw':
                    user_pwd = pwd_v

    print(user_id)
    print(user_pwd)

else:
    empty_list=[]
    print(empty_list)




