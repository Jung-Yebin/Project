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

uid = "aaaaa"
for k, v in users.items():
    if k == uid:
       for k_id, v_id in v.items():
           if k_id == 'id':
               users_id = v_id
       for k_name, v_name in v.items():
           if k_name == 'name':
               users_name = v_name
       for k_gender, v_gender in v.items():
           if k_gender== 'gen':
               users_gender = v_gender
       for k_birth, v_birth in v.items():
           if k_birth == 'birth':
               users_birth = v_birth
       for k_number, v_number in v.items():
           if k_number == 'number':
               users_number = v_number
       for k_job, v_job in v.items():
           if k_job == 'job':
               users_job = v_job

print(users_id, users_name, users_gender)