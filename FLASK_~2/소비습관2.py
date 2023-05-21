import pyrebase
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
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

time = datetime.today().strftime("%Y-%m")
dataFilter = df['date'].str.contains(time)
result = df[dataFilter]
print(result)

cccc = (result['gender'] == '남자') & (result['job'] == '대학생')
print(result[cccc])

ccc222 = result['name'] == uid
print(result[ccc222])


condition = (df['gender'] == user_jender) & (df['job'] == user_job)
category_frequency = df[condition]['category'].mode()[0]
time = datetime.today().strftime("%Y-%m")
dataFilter = df['date'].str.contains(time)
consumption = df[dataFilter]
condition2 = (consumption['gender'] == user_jender) & (consumption['job'] == user_job)

# 나와 같은 조건의 유저 이번달 사용금액
print(consumption[condition2]['cost'].sum())

# 나의 이번달 사용금액
u_consumption = consumption['name'] == uid
print(consumption[u_consumption]['cost'].sum())

# 나와 같은 조건의 유저 이번달 사용빈도
users_thismonth_freq = consumption[condition2]['date']
users_thismonth_freq = len(list(set(users_thismonth_freq)))


#나의 이번달 사용 빈도
u_thismonth_freq = consumption[u_consumption]['date']


users_thismonth_freq = round(30 / users_thismonth_freq)
u_thismonth_freq = round(30 / u_thismonth_freq)

print(users_thismonth_freq)
print(u_thismonth_freq)
#users_average_consum = users_consum_sum / users_thismonth_freq
#u_average_consum = uconsum_sum / u_thismonth_freq

