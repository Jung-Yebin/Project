import pyrebase
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

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

User = db.child("User").get()
Username_list = []
for k, v in User.val().items():
    Username_list.append(k)

user_jender = ''
for key, value in User.val().items():
    if key == uid:
        for jender_k, jender_v in value.items():
            if jender_k == 'gen':
                user_jender = jender_v

user_job = ''
for key, value in User.val().items():
    if key == uid:
        for job_k, job_v in value.items():
            if job_k == 'job':
                user_job = job_v

calendar = db.child("Calendar").get()

na = []
cate = []
co = []
date_list=[]
count = -1

gender_list = []
job_list = []

for k, v in calendar.val().items():
    count = count + 1
    if Username_list[count] in k:
        date = db.child("Calendar").child(Username_list[count]).get()
        for k2, v2 in date.val().items():
            category = db.child("Calendar").child(Username_list[count]).child(k2).get()
            for k3, v3 in category.val().items():
                if None in v3:
                    v3 = {'1': v3[-1]}
                for i in range(
                        len(db.child("Calendar").child(Username_list[count]).child(k2).child(k3).get().val())):
                    num = v3
                for k4, v4 in num.items():

                    for n in range(len(k4)):
                        cost = v4

                        value = db.child("User").child(k).get().val()

                        for k6, v6 in value.items():
                            if k6 == 'gen':
                                gender_list.append(v6)
                            if k6 == 'job':
                                job_list.append(v6)

                        for k5, v5 in cost.items():
                            na.append(k)
                            co.append(v5)
                            cate.append(k3)
                            date_list.append(k2)

co = list(map(int, co))

df = pd.DataFrame()
df['name'] = na
df['date'] = date_list
df['category'] = cate
df['cost'] = co
df['gender'] = gender_list
df['job'] = job_list

uid = 'ababab'
my_df = df['name'] == uid
print(df[my_df])

ucategory = df[my_df]['category'].mode()[0]
print(ucategory)

clist = ['금융' ,'미용&뷰티' ,'문구&디지털',  '통신',  '식비',  '의류&잡화',  '경조사',  '취미&여가',  '문화',  '교육',  '주거&생활',  '건강',  '교통']
Association_category_list = clist
Association_name_list = []
for v in na:
    if v not in Association_name_list:
        Association_name_list.append(v)
Association_name_list = list(set(na))
category = pd.DataFrame(index=Association_name_list, columns=Association_category_list)
category.fillna(0, inplace=True)
for i in range(len(Association_name_list)):
    my_category = df[df['name'] == Association_name_list[i]]['category'].values
    for j in range(len(my_category)):
        category.loc[Association_name_list[i]][my_category[j]] = category.loc[Association_name_list[i]][my_category[j]] + 1


print(category)


print(clist.index(ucategory))
print()
condition1 = category.corr()[ucategory][0:clist.index(ucategory)]
condition2 = category.corr()[ucategory][clist.index(ucategory)+1:len(clist)]
maxvalue = pd.concat([condition1, condition2]).max()

temp_v = pd.concat([condition1, condition2]) == maxvalue
temp_list = pd.concat([condition1, condition2])[temp_v].index.tolist()

print(temp_list)
