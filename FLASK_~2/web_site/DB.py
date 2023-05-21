import pyrebase
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras import models
from keras.engine.functional import Functional
from tensorflow.python.keras.layers import LSTM, Dense


class DBModule:
    def __init__(self):
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
        self.db = firebase.database()

    def login(self, uid, pwd):
        users = self.db.child("User").get().val()
        try:
            userinfo = users[uid]
            if userinfo["pw"] == pwd:
                return True
            else:
                return False
        except:
            return False

    def find_account(self):

        users = self.db.child("User").get().val()

        return users

    def user_detail(self, uid):
        date_list = []
        usage_list = []
        name_list = []
        category_list=[]
        date = self.db.child("Calendar").child(uid).get()
        for k, v in date.val().items():

            for i in range(len(self.db.child("Calendar").child(uid).child().get().val())):
                category = self.db.child("Calendar").child(uid).child(k).get()

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
        users = self.db.child("User").get().val()
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

        # dataFilter = result['date'].str.contains(thisyear)
        # result = result[dataFilter]

        ## 사용자가 올해 소비한 총 금액
        usage_list = result['cost'].to_list()
        usage = sum(usage_list)

        ## 사용자가 이번달 소비한 총 금액
        thismonth = today.strftime("%Y-%m")
        dataFilter = result['date'].str.contains(thismonth)
        uthismonth = result[dataFilter]
        uthismonth = uthismonth['cost'].to_list()
        uthismonth = list(map(int, uthismonth))
        uthismonth = sum(uthismonth)

        ## 사용자가 올해 소비한 총 금액
        uthisyear = result['cost'].to_list()
        uthisyear = list(map(int, uthisyear))
        uthisyear = sum(uthisyear)

        price = list(result['cost'])
        price = np.array(price)

        seq_len = 10
        window_size = seq_len + 1

        values = []
        for i in range(len(price) - seq_len):
            values.append(price[i:i + seq_len])

        # 데이터 정규화
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
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        y_test = values[row:, -1]

        print(result)

        print(x_train.shape)
        print(x_test.shape)

        # 모델 생성
        model = Sequential()

        model.add(LSTM(9, return_sequences=True, input_shape=(9, 1)))
        model.add(LSTM(32, return_sequences=False))
        model.add(Dense(1, activation='linear'))
        model.compile(loss='mse', optimizer='rmsprop',metrics=['accuracy'])

        # 트레이닝
        history = model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=10, epochs=10)

        # 예측
        pred = model.predict(x_test)

        #학습 정확성 & 검증 정확성 시각화
        print(history.history)
        plt.plot(history.history['accuracy'])
        plt.plot(history.history['loss'])
        plt.title('Model accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['accuracy', 'Loss'], loc='upper left')
        plt.show()

        # 역정규화
        min_value = result['cost'].tail(10).min()
        max_value = result['cost'].tail(10).max()

        v = np.array(pred[0])
        y_predict = v[0]
        y_predict = round((y_predict * (max_value - min_value)) + min_value)

        usage_list = list(map(int, usage_list))

        today = datetime.today()
        thisyear = today.strftime("%Y")

        result = pd.DataFrame()
        result['name'] = name_list
        result['date'] = date_list
        result['category'] = category_list
        result['cost'] = usage_list

        dataFilter = result['date'].str.contains(thisyear)
        result = result[dataFilter]

        ## 사용자가 올해 소비한 총 금액
        usage_list = result['cost'].to_list()
        usage = sum(usage_list)

        ## 사용자가 이번달 소비한 총 금액
        thismonth = today.strftime("%Y-%m")
        dataFilter = result['date'].str.contains(thismonth)
        uthismonth = result[dataFilter]
        uthismonth = uthismonth['cost'].to_list()
        uthismonth = list(map(int, uthismonth))
        uthismonth = sum(uthismonth)

        ## 사용자가 올해 소비한 총 금액
        uthisyear = result['cost'].to_list()
        uthisyear = list(map(int, uthisyear))
        uthisyear = sum(uthisyear)


        result.loc[result['name'] == uid, 'name'] = 1

        ucategory = result['category'].mode()[0]

        return ucategory, users_budget, uthismonth, usage, y_predict, uthisyear

    def users_page(self, uid):
        users = self.db.child("User").get().val()

        for k, v in users.items():
            if k == uid:
                for k_id, v_id in v.items():
                    if k_id == 'id':
                        users_id = v_id
                for k_name, v_name in v.items():
                    if k_name == 'name':
                        users_name = v_name
                for k_gender, v_gender in v.items():
                    if k_gender == 'gen':
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

        return users_id,users_name,users_gender,users_birth,users_number,users_job

    def star(self, uid):
        User = self.db.child("User").get()
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

        calendar = self.db.child("Calendar").get()

        name_list = []
        category_list = []
        cost_list = []
        date_list = []
        count = -1

        gender_list = []
        job_list = []

        for k, v in calendar.val().items():
            count = count + 1
            if Username_list[count] in k:
                date = self.db.child("Calendar").child(Username_list[count]).get()
                for k2, v2 in date.val().items():
                    category = self.db.child("Calendar").child(Username_list[count]).child(k2).get()
                    for k3, v3 in category.val().items():
                        if None in v3:
                            v3 = {'1': v3[-1]}
                        for i in range(
                                len(self.db.child("Calendar").child(Username_list[count]).child(k2).child(k3).get().val())):
                            num = v3
                        for k4, v4 in num.items():

                            for n in range(len(k4)):
                                cost = v4

                                value = self.db.child("User").child(k).get().val()

                                for k6, v6 in value.items():
                                    if k6 == 'gen':
                                        gender_list.append(v6)
                                    if k6 == 'job':
                                        job_list.append(v6)

                                for k5, v5 in cost.items():
                                    name_list.append(k)
                                    cost_list.append(v5)
                                    category_list.append(k3)
                                    date_list.append(k2)

        cost_list = list(map(int, cost_list))
        df = pd.DataFrame()
        df['name'] = name_list
        df['date'] = date_list
        df['category'] = category_list
        df['cost'] = cost_list
        df['gender'] = gender_list
        df['job'] = job_list

        # 성별
        condition = (df['gender'] == user_jender)
        gen_category_frequency = df[condition]['category'].mode()[0]
        condition2 = df['category'] == gen_category_frequency
        condition3 = condition & condition2
        users_count = len(df[condition3]['name'].unique())
        print(users_count)
        print(df[condition3]['cost'].sum())
        gen_category_sum = round(df[condition3]['cost'].sum()/users_count)

        # 직업별
        condition = (df['job'] == user_job)
        job_category_frequency = df[condition]['category'].mode()[0]
        condition2 = df['category'] == job_category_frequency
        condition3 = condition & condition2
        print(df[condition3])
        users_count = len(df[condition3]['name'].unique())
        print(df[condition3]['cost'].sum())
        job_category_sum = round(df[condition3]['cost'].sum()/users_count)
        # 성별 & 직업별
        condition = (df['gender'] == user_jender) & (df['job'] == user_job)
        total_category_frequency = df[condition]['category'].mode()[0]
        condition2 = df['category'] == total_category_frequency
        condition3 = condition & condition2
        users_count = len(df[condition3]['name'].unique())
        total_category_sum = round(df[condition3]['cost'].sum()/users_count)

        return gen_category_frequency, gen_category_sum, job_category_frequency, job_category_sum, total_category_frequency, total_category_sum
    def habit(self, uid):

        User = self.db.child("User").get()
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


        # 사용자의 목표 소비 예산
        users = self.db.child("User").get().val()
        for k, v in users.items():
            if k == uid:
                for k_budget, v_budget in v.items():
                    if k_budget == 'budget':
                        users_budget = v_budget

        calendar = self.db.child("Calendar").get()

        name_list = []
        category_list = []
        cost_list = []
        date_list = []
        count = -1

        gender_list = []
        job_list = []

        for k, v in calendar.val().items():
            count = count + 1
            if Username_list[count] in k:
                date = self.db.child("Calendar").child(Username_list[count]).get()
                for k2, v2 in date.val().items():
                    category = self.db.child("Calendar").child(Username_list[count]).child(k2).get()
                    for k3, v3 in category.val().items():
                        if None in v3:
                            v3 = {'1': v3[-1]}
                        for i in range(
                                len(self.db.child("Calendar").child(Username_list[count]).child(k2).child(k3).get().val())):
                            num = v3
                        for k4, v4 in num.items():

                            for n in range(len(k4)):
                                cost = v4

                                value = self.db.child("User").child(k).get().val()

                                for k6, v6 in value.items():
                                    if k6 == 'gen':
                                        gender_list.append(v6)
                                    if k6 == 'job':
                                        job_list.append(v6)

                                for k5, v5 in cost.items():
                                    name_list.append(k)
                                    cost_list.append(v5)
                                    category_list.append(k3)
                                    date_list.append(k2)

        cost_list = list(map(int, cost_list))
        df = pd.DataFrame()
        df['name'] = name_list
        df['date'] = date_list
        df['category'] = category_list
        df['cost'] = cost_list
        df['gender'] = gender_list
        df['job'] = job_list

        #나와 같은 조건의 유저  카테고리 사용빈도
        condition = (df['gender'] == user_jender) & (df['job'] == user_job)
        category_frequency = df[condition]['category'].mode()[0]

        today = datetime.today()
        before_one_month = today - relativedelta(months=1)
        months_ago = before_one_month.strftime("%Y-%m")
        time = datetime.today().strftime("%Y-%m")
        dataFilter = df['date'].str.contains(months_ago)
        consumption = df[dataFilter]
        #category_frequency = consumption[condition]['category'].mode()[0]
        condition2 = (consumption['gender'] == user_jender) & (consumption['job'] == user_job)
        # 나와 같은 조건의 유저 저번달 사용금액
        users_consum_sum = consumption[condition2]['cost'].sum()
        # 나의 저번달 사용금액
        u_consumption = consumption['name'] == uid
        uconsum_sum = consumption[u_consumption]['cost'].sum()
        # 나와 같은 조건의 유저 저번달 사용빈도
        users_lastmonth_freq = consumption[condition2]['date']
        users_lastmonth_freq = len(list(set(users_lastmonth_freq)))
        # 나의 저번달 사용 빈도
        u_lastmonth_freq = consumption[u_consumption]['date']
        u_lastmonth_freq = len(list(set(u_lastmonth_freq)))
        # 나의 이번달 사용금액
        dataFilter2 = df['date'].str.contains(time)
        consumption2 = df[dataFilter2]
        u_this_consumption = consumption2['name'] == uid
        u_thisconsum_sum = consumption2[u_this_consumption]['cost'].sum()
        # 나의 이번달 사용빈도
        u_thismonth_freq = consumption2[u_this_consumption]['date']
        u_thismonth_freq = len(list(set(u_thismonth_freq)))

        if users_lastmonth_freq == 0:
            users_lastmonth_freq = 0
        else:
            users_lastmonth_freq = round(30 / users_lastmonth_freq)

        if u_lastmonth_freq == 0:
            u_lastmonth_freq = 0
        else:
            u_lastmonth_freq = round(30 / u_lastmonth_freq)

        if u_thismonth_freq == 0:
            u_thismonth_freq = 0
        else:
            u_thismonth_freq = round(30 / u_thismonth_freq)

        if users_lastmonth_freq == 0:
            users_average_consum = 0
        else:
            users_average_consum = users_consum_sum / users_lastmonth_freq

        if u_lastmonth_freq == 0:
            u_average_consum = 0
        else:
            u_average_consum = uconsum_sum / u_lastmonth_freq

        # 이번달& 지난달 최대 지출 날짜

        today = datetime.today()
        before_one_month = today - relativedelta(months=1)
        months_ago = before_one_month.strftime("%Y-%m")

        time = datetime.today().strftime("%Y-%m")
        dataFilter = df['date'].str.contains(time)
        result_thismonth = df[dataFilter]
        dataFilter = df['date'].str.contains(months_ago)
        result_lastmonth = df[dataFilter]

        u_lastmonth = result_lastmonth['name'] == uid
        u_thismonth = result_thismonth['name'] == uid

        lastmonth_list = result_lastmonth[u_lastmonth]['date'].unique().tolist()
        thismonth_list = result_thismonth[u_thismonth]['date'].unique().tolist()

        if len(lastmonth_list) == 0 and len(thismonth_list) == 0:
            print(lastmonth_list)
            print(thismonth_list)

        if len(lastmonth_list) != 0 and len(thismonth_list) != 0:
            lastmonth_result = result_lastmonth[u_lastmonth]
            thismonth_result = result_thismonth[u_thismonth]

            lastmonth_cost_list = []
            thismonth_cost_list = []
            for i in range(len(lastmonth_list)):
                lastmonth_cost_list.append(
                    lastmonth_result[result_lastmonth[u_lastmonth]['date'] == lastmonth_list[i]]['cost'].sum())

            for i in range(len(thismonth_list)):
                thismonth_cost_list.append(
                    thismonth_result[result_thismonth[u_thismonth]['date'] == thismonth_list[i]]['cost'].sum())

            lastmonth_max_index = [index for index, item in enumerate(lastmonth_cost_list) if
                                   item == max(thismonth_cost_list)]
            thismonth_max_index = [index for index, item in enumerate(thismonth_cost_list) if
                                   item == max(thismonth_cost_list)]

            if len(lastmonth_max_index) == 0:
                lastmonth_max_index = (lastmonth_cost_list.index(max(lastmonth_cost_list)))

            if len(thismonth_max_index) == 0:
                thismonth_max_index = (thismonth_cost_list.index(max(thismonth_cost_list)))

            if isinstance(lastmonth_max_index, list) == False:
                max_index = []
                max_index.append(lastmonth_max_index)
                lastmonth_max_index = max_index

            if isinstance(thismonth_max_index, list) == False:
                max_index = []
                max_index.append(thismonth_max_index)
                thismonth_max_index = max_index

            lastmonth_result = []
            thismonth_result = []

            for i in range(len(lastmonth_max_index)):
                lastmonth_result.append(lastmonth_list[lastmonth_max_index[i]])

            for i in range(len(thismonth_max_index)):
                thismonth_result.append(thismonth_list[thismonth_max_index[i]])

            lastmonth_list.clear()
            lastmonth_list = lastmonth_result

            thismonth_list.clear()
            thismonth_list = thismonth_result

        #카테고리별 지출 top3

        my_df = df['name'] == uid
        #print(my_df)
        dict_data = df[my_df]['category'].value_counts(ascending=False)
        dict_data = pd.Series(dict_data)
        category_unique = (df[my_df]['category'].value_counts(ascending=False).unique())

        if len(dict_data.index) >= 3:
            for i in range(3):
                print(dict_data.index[i])
        else:
            for i in range(len(dict_data.index)):
                print(dict_data.index[i])

        category_freq = pd.DataFrame()
        category_freq['category'] = dict_data.index
        category_freq['count'] = dict_data.values

        #print(category_freq)

        cate = []

        if len(category_unique) < 3:
            for i in range(len(category_unique)):
                cate.extend(str(i + 1) + "위" +category_freq['category'][category_freq['count'] == category_unique[i]])
        else :
            for i in range(3):
                cate.extend(str(i + 1) + "위" +category_freq['category'][category_freq['count'] == category_unique[i]])

        if df[my_df].empty:
            ucategory = "정보없음"
            templist = "정보없음"
        else:
            my_df = df['name'] == uid
            ucategory = df[my_df]['category'].mode()[0]

            clist = ['금융', '미용&뷰티', '문구&디지털', '통신', '식비', '의류&잡화', '경조사', '취미&여가', '문화', '교육', '주거&생활', '건강', '교통','기타']
            Association_category_list = clist
            Association_name_list = []
            for v in name_list:
                if v not in Association_name_list:
                    Association_name_list.append(v)
            Association_name_list = list(set(name_list))
            category = pd.DataFrame(index=Association_name_list, columns=Association_category_list)
            category.fillna(0, inplace=True)
            for i in range(len(Association_name_list)):
                my_category = df[df['name'] == Association_name_list[i]]['category'].values
                for j in range(len(my_category)):
                    category.loc[Association_name_list[i]][my_category[j]] = category.loc[Association_name_list[i]][my_category[j]] + 1

            print("카테고리:")
            print(category.loc[uid])
            condition1 = category.loc[uid].iloc[0:clist.index(ucategory)]
            condition2 = category.loc[uid].iloc[clist.index(ucategory)+1 : len(clist)]
            maxvalue = pd.concat([condition1, condition2]).max()
            temp_v = pd.concat([condition1, condition2]) == maxvalue
            temp_list = pd.concat([condition1, condition2])[temp_v].index.tolist()
            print(ucategory)
            print(temp_list)

            ## 전체 사용자 대상 연관분석
            users_condition1 = category.corr()[ucategory][0:clist.index(ucategory)]
            users_condition2 = category.corr()[ucategory][clist.index(ucategory) + 1:len(clist)]
            users_maxvalue = pd.concat([users_condition1, users_condition2]).max()
            users_temp_v = pd.concat([users_condition1, users_condition2]) == users_maxvalue
            users_temp_list = pd.concat([users_condition1, users_condition2])[users_temp_v].index.tolist()
            # 최대소비카테고리
            #print(ucategory)
            #print(temp_list)

        return lastmonth_list,cate, users_budget,users_lastmonth_freq, users_average_consum, u_lastmonth_freq, u_average_consum, u_thismonth_freq, u_thisconsum_sum,ucategory, temp_list, users_temp_list

    def category_analysis(self,uid):

        User = self.db.child("User").get()
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

        calendar = self.db.child("Calendar").get()

        name_list = []
        category_list = []
        cost_list = []
        date_list = []
        count = -1

        gender_list = []
        job_list = []

        for k, v in calendar.val().items():
            count = count + 1
            if Username_list[count] in k:
                date = self.db.child("Calendar").child(Username_list[count]).get()
                for k2, v2 in date.val().items():
                    category = self.db.child("Calendar").child(Username_list[count]).child(k2).get()
                    for k3, v3 in category.val().items():
                        if None in v3:
                            v3 = {'1': v3[-1]}
                        for i in range(
                                len(self.db.child("Calendar").child(Username_list[count]).child(k2).child(k3).get().val())):
                            num = v3
                        for k4, v4 in num.items():

                            for n in range(len(k4)):
                                cost = v4

                                value = self.db.child("User").child(k).get().val()

                                for k6, v6 in value.items():
                                    if k6 == 'gen':
                                        gender_list.append(v6)
                                    if k6 == 'job':
                                        job_list.append(v6)

                                for k5, v5 in cost.items():
                                    name_list.append(k)
                                    cost_list.append(v5)
                                    category_list.append(k3)
                                    date_list.append(k2)

        cost_list = list(map(int, cost_list))
        df = pd.DataFrame()
        df['name'] = name_list
        df['date'] = date_list
        df['category'] = category_list
        df['cost'] = cost_list
        df['gender'] = gender_list
        df['job'] = job_list

        today = datetime.today()
        before_one_month = today - relativedelta(months=1)
        months_ago = before_one_month.strftime("%Y-%m")
        dataFilter = df['date'].str.contains(months_ago)
        result_lastmonth = df[dataFilter]

        before_two_month = today - relativedelta(months=2)
        two_months_ago = before_two_month.strftime("%Y-%m")
        dataFilter = df['date'].str.contains(two_months_ago)
        result_two_month_ago = df[dataFilter]

        before_three_month = today - relativedelta(months=3)
        three_months_ago = before_three_month.strftime("%Y-%m")
        dataFilter = df['date'].str.contains(three_months_ago)
        result_three_month_ago = df[dataFilter]

        before_four_month = today - relativedelta(months=4)
        four_months_ago = before_four_month.strftime("%Y-%m")
        dataFilter = df['date'].str.contains(four_months_ago)
        result_four_month_ago = df[dataFilter]

        before_five_month = today - relativedelta(months=5)
        five_months_ago = before_five_month.strftime("%Y-%m")
        dataFilter = df['date'].str.contains(five_months_ago)
        result_five_month_ago = df[dataFilter]

        time = datetime.today().strftime("%Y-%m")
        dataFilter = df['date'].str.contains(time)
        result_thismonth = df[dataFilter]

        u_this_df = result_thismonth[result_thismonth['name'] == uid]
        u_df = result_lastmonth[result_lastmonth['name'] == uid]
        u_two_df = result_two_month_ago[result_two_month_ago['name'] == uid]
        u_three_df = result_three_month_ago[result_three_month_ago['name'] == uid]
        u_four_df = result_four_month_ago[result_four_month_ago['name'] == uid]
        u_five_df = result_five_month_ago[result_five_month_ago['name'] == uid]

        if u_df.empty:
            lastmonth_food = 0
            lastmonth_bank = 0
            lastmonth_beauty = 0
            lastmonth_digital = 0
            lastmonth_communication = 0
            lastmonth_congratulate = 0
            lastmonth_leisure = 0
            lastmonth_culture = 0
            lastmonth_education = 0
            lastmonth_live = 0
            lastmonth_health= 0
            lastmonth_traffic= 0
            lastmonth_cloth = 0
            lastmonth_etc = 0
            lastmonth_food_rate = 0
            lastmonth_bank_rate = 0
            lastmonth_beauty_rate = 0
            lastmonth_digital_rate = 0
            lastmonth_communication_rate = 0
            lastmonth_congratulate_rate = 0
            lastmonth_leisure_rate = 0
            lastmonth_culture_rate = 0
            lastmonth_education_rate = 0
            lastmonth_live_rate = 0
            lastmonth_health_rate = 0
            lastmonth_traffic_rate = 0
            lastmonth_cloth_rate = 0
            lastmonth_etc_rate = 0
        else:
            lastmonth_sum = u_df['cost'].sum()
            lastmonth_food = u_df[u_df['category'] == '식비']['cost'].sum()
            lastmonth_bank = u_df[u_df['category'] == '금융']['cost'].sum()
            lastmonth_beauty = u_df[u_df['category'] == '미용&뷰티']['cost'].sum()
            lastmonth_digital = u_df[u_df['category'] == '문구&디지털']['cost'].sum()
            lastmonth_communication = u_df[u_df['category'] == '통신']['cost'].sum()
            lastmonth_congratulate = u_df[u_df['category'] == '경조사']['cost'].sum()
            lastmonth_leisure = u_df[u_df['category'] == '취미&여가']['cost'].sum()
            lastmonth_culture = u_df[u_df['category'] == '문화']['cost'].sum()
            lastmonth_education = u_df[u_df['category'] == '교육']['cost'].sum()
            lastmonth_live = u_df[u_df['category'] == '주거&생활']['cost'].sum()
            lastmonth_health = u_df[u_df['category'] == '건강']['cost'].sum()
            lastmonth_traffic = u_df[u_df['category'] == '교통']['cost'].sum()
            lastmonth_cloth = u_df[u_df['category'] == '의류&잡화']['cost'].sum()
            lastmonth_etc = u_df[u_df['category'] == '기타']['cost'].sum()

            try:
                lastmonth_food_rate = round((lastmonth_food / lastmonth_sum) * 100)
            except:
                lastmonth_food_rate = 0
            try:
                lastmonth_bank_rate = round((lastmonth_bank / lastmonth_sum) * 100)
            except:
                lastmonth_bank_rate = 0
            try:
                lastmonth_beauty_rate = round((lastmonth_beauty / lastmonth_sum) * 100)
            except:
                lastmonth_beauty_rate = 0
            try:
                lastmonth_digital_rate = round((lastmonth_digital / lastmonth_sum) * 100)
            except:
                lastmonth_digital_rate = 0
            try:
                lastmonth_communication_rate = round((lastmonth_communication / lastmonth_sum) * 100)
            except:
                lastmonth_communication_rate = 0
            try:
                lastmonth_congratulate_rate = round((lastmonth_congratulate / lastmonth_sum) * 100)
            except:
                lastmonth_congratulate_rate = 0
            try:
                lastmonth_leisure_rate = round((lastmonth_leisure / lastmonth_sum) * 100)
            except:
                lastmonth_leisure_rate = 0
            try:
                lastmonth_culture_rate = round((lastmonth_culture / lastmonth_sum) * 100)
            except:
                lastmonth_culture_rate = 0
            try:
                lastmonth_education_rate = round((lastmonth_education / lastmonth_sum) * 100)
            except:
                lastmonth_education_rate = 0
            try:
                lastmonth_live_rate = round((lastmonth_live / lastmonth_sum) * 100)
            except:
                lastmonth_live_rate = 0
            try:
                lastmonth_health_rate = round((lastmonth_health / lastmonth_sum) * 100)
            except:
                lastmonth_health_rate = 0
            try:
                lastmonth_traffic_rate = round((lastmonth_traffic / lastmonth_sum) * 100)
            except:
                lastmonth_traffic_rate = 0
            try:
                lastmonth_cloth_rate = round((lastmonth_cloth / lastmonth_sum) * 100)
            except:
                lastmonth_cloth_rate = 0
            try:
                lastmonth_etc_rate = round((lastmonth_etc / lastmonth_sum) * 100)
            except:
                lastmonth_etc_rate = 0

        if u_two_df.empty:
            twomonth_food= 0
            twomonth_bank = 0
            twomonth_beauty = 0
            twomonth_digital = 0
            twomonth_communication = 0
            twomonth_congratulate = 0
            twomonth_leisure = 0
            twomonth_culture = 0
            twomonth_education = 0
            twomonth_live = 0
            twomonth_health = 0
            twomonth_traffic = 0
            twomonth_cloth = 0
            twomonth_etc = 0
            twomonth_food_rate = 0
            twomonth_bank_rate = 0
            twomonth_beauty_rate = 0
            twomonth_digital_rate = 0
            twomonth_communication_rate = 0
            twomonth_congratulate_rate = 0
            twomonth_leisure_rate = 0
            twomonth_culture_rate = 0
            twomonth_education_rate = 0
            twomonth_live_rate = 0
            twomonth_health_rate = 0
            twomonth_traffic_rate = 0
            twomonth_cloth_rate = 0
            twomonth_etc_rate = 0
        else:
            twomonth_sum = u_two_df['cost'].sum()
            twomonth_food = u_two_df[u_two_df['category'] == '식비']['cost'].sum()
            twomonth_bank = u_two_df[u_two_df['category'] == '금융']['cost'].sum()
            twomonth_beauty = u_two_df[u_two_df['category'] == '미용&뷰티']['cost'].sum()
            twomonth_digital = u_two_df[u_two_df['category'] == '문구&디지털']['cost'].sum()
            twomonth_communication = u_two_df[u_two_df['category'] == '통신']['cost'].sum()
            twomonth_congratulate = u_two_df[u_two_df['category'] == '경조사']['cost'].sum()
            twomonth_leisure = u_two_df[u_two_df['category'] == '취미&여가']['cost'].sum()
            twomonth_culture = u_two_df[u_two_df['category'] == '문화']['cost'].sum()
            twomonth_education = u_two_df[u_two_df['category'] == '교육']['cost'].sum()
            twomonth_live = u_two_df[u_two_df['category'] == '주거&생활']['cost'].sum()
            twomonth_health = u_two_df[u_two_df['category'] == '건강']['cost'].sum()
            twomonth_traffic = u_two_df[u_two_df['category'] == '교통']['cost'].sum()
            twomonth_cloth = u_two_df[u_two_df['category'] == '의류&잡화']['cost'].sum()
            twomonth_etc = u_two_df[u_two_df['category'] == '기타']['cost'].sum()

            try:
                twomonth_food_rate = round((twomonth_food / twomonth_sum) * 100)
            except:
                twomonth_food_rate = 0
            try:
                twomonth_bank_rate = round((twomonth_bank / twomonth_sum) * 100)
            except:
                twomonth_bank_rate = 0
            try:
                twomonth_beauty_rate = round((twomonth_beauty / twomonth_sum) * 100)
            except:
                twomonth_beauty_rate = 0
            try:
                twomonth_digital_rate = round((twomonth_digital / twomonth_sum) * 100)
            except:
                twomonth_digital_rate = 0
            try:
                twomonth_communication_rate = round((twomonth_communication / twomonth_sum) * 100)
            except:
                twomonth_communication_rate = 0
            try:
                twomonth_congratulate_rate = round((twomonth_congratulate / twomonth_sum) * 100)
            except:
                twomonth_congratulate_rate = 0
            try:
                twomonth_leisure_rate = round((twomonth_leisure / twomonth_sum) * 100)
            except:
                twomonth_leisure_rate = 0
            try:
                twomonth_culture_rate = round((twomonth_culture / twomonth_sum) * 100)
            except:
                twomonth_culture_rate = 0
            try:
                twomonth_education_rate = round((twomonth_education / twomonth_sum) * 100)
            except:
                twomonth_education_rate = 0
            try:
                twomonth_live_rate = round((twomonth_live / twomonth_sum) * 100)
            except:
                twomonth_live_rate = 0
            try:
                twomonth_health_rate = round((twomonth_health / twomonth_sum) * 100)
            except:
                twomonth_health_rate = 0
            try:
                twomonth_traffic_rate = round((twomonth_traffic / twomonth_sum) * 100)
            except:
                twomonth_traffic_rate = 0
            try:
                twomonth_cloth_rate = round((twomonth_cloth / twomonth_sum) * 100)
            except:
                twomonth_cloth_rate = 0
            try:
                twomonth_etc_rate = round((twomonth_etc / twomonth_sum) * 100)
            except:
                twomonth_etc_rate = 0

        if u_three_df.empty:
            threemonth_food = 0
            threemonth_bank = 0
            threemonth_beauty = 0
            threemonth_digital = 0
            threemonth_communication = 0
            threemonth_congratulate = 0
            threemonth_leisure = 0
            threemonth_culture = 0
            threemonth_education = 0
            threemonth_live = 0
            threemonth_health = 0
            threemonth_traffic = 0
            threemonth_cloth = 0
            threemonth_etc = 0
            threemonth_food_rate = 0
            threemonth_bank_rate = 0
            threemonth_beauty_rate = 0
            threemonth_digital_rate = 0
            threemonth_communication_rate = 0
            threemonth_congratulate_rate = 0
            threemonth_leisure_rate = 0
            threemonth_culture_rate = 0
            threemonth_education_rate = 0
            threemonth_live_rate = 0
            threemonth_health_rate = 0
            threemonth_traffic_rate = 0
            threemonth_cloth_rate = 0
            threemonth_etc_rate = 0
        else:
            threemonth_sum = u_three_df['cost'].sum()
            threemonth_food = u_three_df[u_three_df['category'] == '식비']['cost'].sum()
            threemonth_bank = u_three_df[u_three_df['category'] == '금융']['cost'].sum()
            threemonth_beauty = u_three_df[u_three_df['category'] == '미용&뷰티']['cost'].sum()
            threemonth_digital = u_three_df[u_three_df['category'] == '문구&디지털']['cost'].sum()
            threemonth_communication = u_three_df[u_three_df['category'] == '통신']['cost'].sum()
            threemonth_congratulate = u_three_df[u_three_df['category'] == '경조사']['cost'].sum()
            threemonth_leisure = u_three_df[u_three_df['category'] == '취미&여가']['cost'].sum()
            threemonth_culture = u_three_df[u_three_df['category'] == '문화']['cost'].sum()
            threemonth_education = u_three_df[u_three_df['category'] == '교육']['cost'].sum()
            threemonth_live = u_three_df[u_three_df['category'] == '주거&생활']['cost'].sum()
            threemonth_health = u_three_df[u_three_df['category'] == '건강']['cost'].sum()
            threemonth_traffic = u_three_df[u_three_df['category'] == '교통']['cost'].sum()
            threemonth_cloth = u_three_df[u_three_df['category'] == '의류&잡화']['cost'].sum()
            threemonth_etc = u_three_df[u_three_df['category'] == '기타']['cost'].sum()

            try:
                threemonth_food_rate = round((threemonth_food / threemonth_sum) * 100)
            except:
                threemonth_food_rate = 0
            try:
                threemonth_bank_rate = round((threemonth_bank / threemonth_sum) * 100)
            except:
                threemonth_bank_rate = 0
            try:
                threemonth_beauty_rate = round((threemonth_beauty / threemonth_sum) * 100)
            except:
                threemonth_beauty_rate = 0
            try:
                threemonth_digital_rate = round((threemonth_digital / threemonth_sum) * 100)
            except:
                threemonth_digital_rate = 0
            try:
                threemonth_communication_rate = round((threemonth_communication / threemonth_sum) * 100)
            except:
                threemonth_communication_rate = 0
            try:
                threemonth_congratulate_rate = round((threemonth_congratulate / threemonth_sum) * 100)
            except:
                threemonth_congratulate_rate = 0
            try:
                threemonth_leisure_rate = round((threemonth_leisure / threemonth_sum) * 100)
            except:
                threemonth_leisure_rate = 0
            try:
                threemonth_culture_rate = round((threemonth_culture / threemonth_sum) * 100)
            except:
                threemonth_culture_rate = 0
            try:
                threemonth_education_rate = round((threemonth_education / threemonth_sum) * 100)
            except:
                threemonth_education_rate = 0
            try:
                threemonth_live_rate = round((threemonth_live / threemonth_sum) * 100)
            except:
                threemonth_live_rate = 0
            try:
                threemonth_health_rate = round((threemonth_health / threemonth_sum) * 100)
            except:
                threemonth_health_rate = 0
            try:
                threemonth_traffic_rate = round((threemonth_traffic / threemonth_sum) * 100)
            except:
                threemonth_traffic_rate = 0
            try:
                threemonth_cloth_rate = round((threemonth_cloth / threemonth_sum) * 100)
            except:
                threemonth_cloth_rate = 0
            try:
                threemonth_etc_rate = round((threemonth_etc / threemonth_sum) * 100)
            except:
                threemonth_etc_rate = 0

        if u_four_df.empty:
            fourmonth_food = 0
            fourmonth_bank = 0
            fourmonth_beauty = 0
            fourmonth_digital = 0
            fourmonth_communication = 0
            fourmonth_congratulate = 0
            fourmonth_leisure = 0
            fourmonth_culture = 0
            fourmonth_education = 0
            fourmonth_live = 0
            fourmonth_health = 0
            fourmonth_traffic = 0
            fourmonth_cloth = 0
            fourmonth_etc = 0
            fourmonth_food_rate = 0
            fourmonth_bank_rate = 0
            fourmonth_beauty_rate = 0
            fourmonth_digital_rate = 0
            fourmonth_communication_rate = 0
            fourmonth_congratulate_rate = 0
            fourmonth_leisure_rate = 0
            fourmonth_culture_rate = 0
            fourmonth_education_rate = 0
            fourmonth_live_rate = 0
            fourmonth_health_rate = 0
            fourmonth_traffic_rate = 0
            fourmonth_cloth_rate = 0
            fourmonth_etc_rate = 0
        else:
            fourmonth_sum = u_four_df['cost'].sum()
            fourmonth_food = u_four_df[u_four_df['category'] == '식비']['cost'].sum()
            fourmonth_bank = u_four_df[u_four_df['category'] == '금융']['cost'].sum()
            fourmonth_beauty = u_four_df[u_four_df['category'] == '미용&뷰티']['cost'].sum()
            fourmonth_digital = u_four_df[u_four_df['category'] == '문구&디지털']['cost'].sum()
            fourmonth_communication = u_four_df[u_four_df['category'] == '통신']['cost'].sum()
            fourmonth_congratulate = u_four_df[u_four_df['category'] == '경조사']['cost'].sum()
            fourmonth_leisure = u_four_df[u_four_df['category'] == '취미&여가']['cost'].sum()
            fourmonth_culture = u_four_df[u_four_df['category'] == '문화']['cost'].sum()
            fourmonth_education = u_four_df[u_four_df['category'] == '교육']['cost'].sum()
            fourmonth_live = u_four_df[u_four_df['category'] == '주거&생활']['cost'].sum()
            fourmonth_health = u_four_df[u_four_df['category'] == '건강']['cost'].sum()
            fourmonth_traffic = u_four_df[u_four_df['category'] == '교통']['cost'].sum()
            fourmonth_cloth = u_four_df[u_four_df['category'] == '의류&잡화']['cost'].sum()
            fourmonth_etc = u_four_df[u_four_df['category'] == '기타']['cost'].sum()

            try:
                fourmonth_food_rate = round((fourmonth_food / fourmonth_sum) * 100)
            except:
                fourmonth_food_rate = 0
            try:
                fourmonth_bank_rate = round((fourmonth_bank / fourmonth_sum) * 100)
            except:
                fourmonth_bank_rate = 0
            try:
                fourmonth_beauty_rate = round((fourmonth_beauty / fourmonth_sum) * 100)
            except:
                fourmonth_beauty_rate = 0
            try:
                fourmonth_digital_rate = round((fourmonth_digital / fourmonth_sum) * 100)
            except:
                fourmonth_digital_rate = 0
            try:
                fourmonth_communication_rate = round((fourmonth_communication / fourmonth_sum) * 100)
            except:
                fourmonth_communication_rate = 0
            try:
                fourmonth_congratulate_rate = round((fourmonth_congratulate / fourmonth_sum) * 100)
            except:
                fourmonth_congratulate_rate = 0
            try:
                fourmonth_leisure_rate = round((fourmonth_leisure / fourmonth_sum) * 100)
            except:
                fourmonth_leisure_rate = 0
            try:
                fourmonth_culture_rate = round((fourmonth_culture / fourmonth_sum) * 100)
            except:
                fourmonth_culture_rate = 0
            try:
                fourmonth_education_rate = round((fourmonth_education / fourmonth_sum) * 100)
            except:
                fourmonth_education_rate = 0
            try:
                fourmonth_live_rate = round((fourmonth_live / fourmonth_sum) * 100)
            except:
                fourmonth_live_rate = 0
            try:
                fourmonth_health_rate = round((fourmonth_health / fourmonth_sum) * 100)
            except:
                fourmonth_health_rate = 0
            try:
                fourmonth_traffic_rate = round((fourmonth_traffic / fourmonth_sum) * 100)
            except:
                fourmonth_traffic_rate = 0
            try:
                fourmonth_cloth_rate = round((fourmonth_cloth / fourmonth_sum) * 100)
            except:
                fourmonth_cloth_rate = 0
            try:
                fourmonth_etc_rate = round((fourmonth_etc / fourmonth_sum) * 100)
            except:
                fourmonth_etc_rate = 0

        if u_five_df.empty:
            fivemonth_food = 0
            fivemonth_bank = 0
            fivemonth_beauty = 0
            fivemonth_digital = 0
            fivemonth_communication = 0
            fivemonth_congratulate = 0
            fivemonth_leisure = 0
            fivemonth_culture = 0
            fivemonth_education = 0
            fivemonth_live = 0
            fivemonth_health = 0
            fivemonth_traffic = 0
            fivemonth_cloth = 0
            fivemonth_etc = 0
            fivemonth_food_rate = 0
            fivemonth_bank_rate = 0
            fivemonth_beauty_rate = 0
            fivemonth_digital_rate = 0
            fivemonth_communication_rate = 0
            fivemonth_congratulate_rate = 0
            fivemonth_leisure_rate = 0
            fivemonth_culture_rate = 0
            fivemonth_education_rate = 0
            fivemonth_live_rate = 0
            fivemonth_health_rate = 0
            fivemonth_traffic_rate = 0
            fivemonth_cloth_rate = 0
            fivemonth_etc_rate = 0
        else:
            fivemonth_sum = u_five_df['cost'].sum()
            fivemonth_food = u_five_df[u_five_df['category'] == '식비']['cost'].sum()
            fivemonth_bank = u_five_df[u_five_df['category'] == '금융']['cost'].sum()
            fivemonth_beauty = u_five_df[u_five_df['category'] == '미용&뷰티']['cost'].sum()
            fivemonth_digital = u_five_df[u_five_df['category'] == '문구&디지털']['cost'].sum()
            fivemonth_communication = u_five_df[u_five_df['category'] == '통신']['cost'].sum()
            fivemonth_congratulate = u_five_df[u_five_df['category'] == '경조사']['cost'].sum()
            fivemonth_leisure = u_five_df[u_five_df['category'] == '취미&여가']['cost'].sum()
            fivemonth_culture = u_five_df[u_five_df['category'] == '문화']['cost'].sum()
            fivemonth_education = u_five_df[u_five_df['category'] == '교육']['cost'].sum()
            fivemonth_live = u_five_df[u_five_df['category'] == '주거&생활']['cost'].sum()
            fivemonth_health = u_five_df[u_five_df['category'] == '건강']['cost'].sum()
            fivemonth_traffic = u_five_df[u_five_df['category'] == '교통']['cost'].sum()
            fivemonth_cloth = u_five_df[u_five_df['category'] == '의류&잡화']['cost'].sum()
            fivemonth_etc = u_five_df[u_five_df['category'] == '기타']['cost'].sum()

            try:
                fivemonth_food_rate = round((fivemonth_food / fivemonth_sum) * 100)
            except:
                fivemonth_food_rate = 0
            try:
                fivemonth_bank_rate = round((fivemonth_bank / fivemonth_sum) * 100)
            except:
                fivemonth_bank_rate = 0
            try:
                fivemonth_beauty_rate = round((fivemonth_beauty / fivemonth_sum) * 100)
            except:
                fivemonth_beauty_rate = 0
            try:
                fivemonth_digital_rate = round((fivemonth_digital / fivemonth_sum) * 100)
            except:
                fivemonth_digital_rate = 0
            try:
                fivemonth_communication_rate = round((fivemonth_communication / fivemonth_sum) * 100)
            except:
                fivemonth_communication_rate = 0
            try:
                fivemonth_congratulate_rate = round((fivemonth_congratulate / fivemonth_sum) * 100)
            except:
                fivemonth_congratulate_rate = 0
            try:
                fivemonth_leisure_rate = round((fivemonth_leisure / fivemonth_sum) * 100)
            except:
                fivemonth_leisure_rate = 0
            try:
                fivemonth_culture_rate = round((fivemonth_culture / fivemonth_sum) * 100)
            except:
                fivemonth_culture_rate = 0
            try:
                fivemonth_education_rate = round((fivemonth_education / fivemonth_sum) * 100)
            except:
                fivemonth_education_rate = 0
            try:
                fivemonth_live_rate = round((fivemonth_live / fivemonth_sum) * 100)
            except:
                fivemonth_live_rate = 0
            try:
                fivemonth_health_rate = round((fivemonth_health / fivemonth_sum) * 100)
            except:
                fivemonth_health_rate = 0
            try:
                fivemonth_traffic_rate = round((fivemonth_traffic / fivemonth_sum) * 100)
            except:
                fivemonth_traffic_rate = 0
            try:
                fivemonth_cloth_rate = round((fivemonth_cloth / fivemonth_sum) * 100)
            except:
                fivemonth_cloth_rate = 0
            try:
                fivemonth_etc_rate = round((fivemonth_etc / fivemonth_sum) * 100)
            except:
                fivemonth_etc_rate = 0

        thismonth_food = u_this_df[u_this_df['category'] == '식비']['cost'].sum()
        thismonth_bank = u_this_df[u_this_df['category'] == '금융']['cost'].sum()
        thismonth_beauty = u_this_df[u_this_df['category'] == '미용&뷰티']['cost'].sum()
        thismonth_digital = u_this_df[u_this_df['category'] == '문구&디지털']['cost'].sum()
        thismonth_communication = u_this_df[u_this_df['category'] == '통신']['cost'].sum()
        thismonth_congratulate = u_this_df[u_this_df['category'] == '경조사']['cost'].sum()
        thismonth_leisure = u_this_df[u_this_df['category'] == '취미&여가']['cost'].sum()
        thismonth_culture = u_this_df[u_this_df['category'] == '문화']['cost'].sum()
        thismonth_education = u_this_df[u_this_df['category'] == '교육']['cost'].sum()
        thismonth_live = u_this_df[u_this_df['category'] == '주거&생활']['cost'].sum()
        thismonth_health = u_this_df[u_this_df['category'] == '건강']['cost'].sum()
        thismonth_traffic = u_this_df[u_this_df['category'] == '교통']['cost'].sum()
        thismonth_cloth = u_this_df[u_this_df['category'] == '의류&잡화']['cost'].sum()
        thismonth_etc = u_this_df[u_this_df['category'] == '기타']['cost'].sum()



        return thismonth_food, thismonth_bank, thismonth_beauty, thismonth_digital, thismonth_communication, thismonth_congratulate,thismonth_leisure,thismonth_culture,thismonth_education,thismonth_live,thismonth_health,thismonth_traffic,thismonth_cloth,thismonth_etc,lastmonth_food, lastmonth_bank, lastmonth_beauty, lastmonth_digital, lastmonth_communication, lastmonth_congratulate,lastmonth_leisure,lastmonth_culture,lastmonth_education,lastmonth_live,lastmonth_health,lastmonth_traffic,lastmonth_cloth,lastmonth_etc, lastmonth_food_rate, lastmonth_bank_rate, lastmonth_beauty_rate, lastmonth_digital_rate, lastmonth_communication_rate, lastmonth_congratulate_rate,lastmonth_leisure_rate,lastmonth_culture_rate,lastmonth_education_rate,lastmonth_live_rate,lastmonth_health_rate,lastmonth_traffic_rate,lastmonth_cloth_rate,lastmonth_etc_rate,twomonth_food, twomonth_bank, twomonth_beauty, twomonth_digital, twomonth_communication, twomonth_congratulate,twomonth_leisure,twomonth_culture,twomonth_education,twomonth_live,twomonth_health,twomonth_traffic,twomonth_cloth,twomonth_etc,threemonth_food, threemonth_bank, threemonth_beauty, threemonth_digital, threemonth_communication, threemonth_congratulate,threemonth_leisure,threemonth_culture,threemonth_education,threemonth_live,threemonth_health,threemonth_traffic,threemonth_cloth,threemonth_etc,fourmonth_food, fourmonth_bank, fourmonth_beauty, fourmonth_digital, fourmonth_communication, fourmonth_congratulate,fourmonth_leisure,fourmonth_culture,fourmonth_education,fourmonth_live,fourmonth_health,fourmonth_traffic,fourmonth_cloth,fourmonth_etc,fivemonth_food, fivemonth_bank, fivemonth_beauty, fivemonth_digital, fivemonth_communication, fivemonth_congratulate,fivemonth_leisure,fivemonth_culture,fivemonth_education,fivemonth_live,fivemonth_health,fivemonth_traffic,fivemonth_cloth,fivemonth_etc,twomonth_food_rate, twomonth_bank_rate, twomonth_beauty_rate, twomonth_digital_rate, twomonth_communication_rate, twomonth_congratulate_rate,twomonth_leisure_rate,twomonth_culture_rate,twomonth_education_rate,twomonth_live_rate,twomonth_health_rate,twomonth_traffic_rate,twomonth_cloth_rate,twomonth_etc_rate,threemonth_food_rate, threemonth_bank_rate, threemonth_beauty_rate, threemonth_digital_rate, threemonth_communication_rate, threemonth_congratulate_rate,threemonth_leisure_rate,threemonth_culture_rate,threemonth_education_rate,threemonth_live_rate,threemonth_health_rate,threemonth_traffic_rate,threemonth_cloth_rate,threemonth_etc_rate,fourmonth_food_rate, fourmonth_bank_rate, fourmonth_beauty_rate, fourmonth_digital_rate, fourmonth_communication_rate, fourmonth_congratulate_rate,fourmonth_leisure_rate,fourmonth_culture_rate,fourmonth_education_rate,fourmonth_live_rate,fourmonth_health_rate,fourmonth_traffic_rate,fourmonth_cloth_rate,fourmonth_etc_rate,fivemonth_food_rate, fivemonth_bank_rate, fivemonth_beauty_rate, fivemonth_digital_rate, fivemonth_communication_rate, fivemonth_congratulate_rate,fivemonth_leisure_rate,fivemonth_culture_rate,fivemonth_education_rate,fivemonth_live_rate,fivemonth_health_rate,fivemonth_traffic_rate,fivemonth_cloth_rate,fivemonth_etc_rate

    def association_analysis(self,uid):

        User = self.db.child("User").get()
        Username_list = []
        for k, v in User.val().items():
            Username_list.append(k)

        calendar = self.db.child("Calendar").get()

        na = []
        cate = []
        co = []
        date_list = []
        count = -1

        gender_list = []
        job_list = []

        for k, v in calendar.val().items():
            count = count + 1
            if Username_list[count] in k:
                date = self.db.child("Calendar").child(Username_list[count]).get()
                for k2, v2 in date.val().items():
                    category = self.db.child("Calendar").child(Username_list[count]).child(k2).get()
                    for k3, v3 in category.val().items():
                        if None in v3:
                            v3 = {'1': v3[-1]}
                        for i in range(
                                len(self.db.child("Calendar").child(Username_list[count]).child(k2).child(k3).get().val())):
                            num = v3
                        for k4, v4 in num.items():

                            for n in range(len(k4)):
                                cost = v4

                                value = self.db.child("User").child(k).get().val()

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

        my_df = df['name'] == uid

        if df[my_df].empty:
            ucategory = "정보없음"
            templist = "정보없음"
        else:
            ucategory = df[my_df]['category'].mode()[0]

            my_df = df['name'] == uid
            ucategory = df[my_df]['category'].mode()[0]

            clist = ['금융', '미용&뷰티', '문구&디지털', '통신', '식비', '의류&잡화', '경조사', '취미&여가', '문화', '교육', '주거&생활', '건강', '교통',
                     '기타']
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
                    category.loc[Association_name_list[i]][my_category[j]] = category.loc[Association_name_list[i]][
                                                                                 my_category[j]] + 1

            print(category)

            print(clist.index(ucategory))
            print()
            condition1 = category.corr()[ucategory][0:clist.index(ucategory)]
            condition2 = category.corr()[ucategory][clist.index(ucategory) + 1:len(clist)]
            maxvalue = pd.concat([condition1, condition2]).max()

            temp_v = pd.concat([condition1, condition2]) == maxvalue
            temp_list = pd.concat([condition1, condition2])[temp_v].index.tolist()

            # 최대소비카테고리
            print(ucategory)

            print(temp_list)

        return ucategory, temp_list

    def users_consumption(self, uid):

        User = self.db.child("User").get()
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

        calendar = self.db.child("Calendar").get()

        name_list = []
        category_list = []
        cost_list = []
        date_list = []
        count = -1

        gender_list = []
        job_list = []

        for k, v in calendar.val().items():
            count = count + 1
            if Username_list[count] in k:
                date = self.db.child("Calendar").child(Username_list[count]).get()
                for k2, v2 in date.val().items():
                    category = self.db.child("Calendar").child(Username_list[count]).child(k2).get()
                    for k3, v3 in category.val().items():
                        if None in v3:
                            v3 = {'1': v3[-1]}
                        for i in range(
                                len(self.db.child("Calendar").child(Username_list[count]).child(k2).child(k3).get().val())):
                            num = v3
                        for k4, v4 in num.items():

                            for n in range(len(k4)):
                                cost = v4

                                value = self.db.child("User").child(k).get().val()

                                for k6, v6 in value.items():
                                    if k6 == 'gen':
                                        gender_list.append(v6)
                                    if k6 == 'job':
                                        job_list.append(v6)

                                for k5, v5 in cost.items():
                                    name_list.append(k)
                                    cost_list.append(v5)
                                    category_list.append(k3)
                                    date_list.append(k2)

        cost_list = list(map(int, cost_list))
        df = pd.DataFrame()
        df['name'] = name_list
        df['date'] = date_list
        df['category'] = category_list
        df['cost'] = cost_list
        df['gender'] = gender_list
        df['job'] = job_list

        #나와 같은 조건의 유저  카테고리 사용빈도
        condition = (df['gender'] == user_jender) & (df['job'] == user_job)
        category_frequency = df[condition]['category'].mode()[0]

        today = datetime.today()
        before_one_month = today - relativedelta(months=1)
        months_ago = before_one_month.strftime("%Y-%m")
        time = datetime.today().strftime("%Y-%m")
        dataFilter = df['date'].str.contains(months_ago)
        consumption = df[dataFilter]
        #category_frequency = consumption[condition]['category'].mode()[0]
        condition2 = (consumption['gender'] == user_jender) & (consumption['job'] == user_job)
        # 나와 같은 조건의 유저 저번달 사용금액
        users_consum_sum = consumption[condition2]['cost'].sum()
        # 나의 저번달 사용금액
        u_consumption = consumption['name'] == uid
        uconsum_sum = consumption[u_consumption]['cost'].sum()
        # 나와 같은 조건의 유저 저번달 사용빈도
        users_lastmonth_freq = consumption[condition2]['date']
        users_lastmonth_freq = len(list(set(users_lastmonth_freq)))
        # 나의 저번달 사용 빈도
        u_lastmonth_freq = consumption[u_consumption]['date']
        u_lastmonth_freq = len(list(set(u_lastmonth_freq)))

        if users_lastmonth_freq == 0:
            users_lastmonth_freq = 0
        else:
            users_lastmonth_freq = round(30 / users_lastmonth_freq)
        if u_lastmonth_freq == 0:
            u_lastmonth_freq = 0
        else:
            u_lastmonth_freq = round(30 / u_lastmonth_freq)

        if users_lastmonth_freq == 0:
            users_average_consum = 0
        else:
            users_average_consum = users_consum_sum / users_lastmonth_freq

        if u_lastmonth_freq == 0:
            u_average_consum = 0
        else:
            u_average_consum = uconsum_sum / u_lastmonth_freq


        #카테고리 연관분석

        my_df = df['name'] == uid
        ucategory = df[my_df]['category'].mode()[0]

        clist = ['금융', '미용&뷰티', '문구&디지털', '통신', '식비', '의류&잡화', '경조사', '취미&여가', '문화', '교육', '주거&생활', '건강', '교통']
        Association_category_list = clist
        Association_name_list = []
        for v in name_list:
            if v not in Association_name_list:
                Association_name_list.append(v)
        Association_name_list = list(set(name_list))
        category = pd.DataFrame(index=Association_name_list, columns=Association_category_list)
        category.fillna(0, inplace=True)
        for i in range(len(Association_name_list)):
            my_category = df[df['name'] == Association_name_list[i]]['category'].values
            for j in range(len(my_category)):
                category.loc[Association_name_list[i]][my_category[j]] = category.loc[Association_name_list[i]][my_category[j]] + 1

        condition1 = category.corr()[ucategory][0:clist.index(ucategory)]
        condition2 = category.corr()[ucategory][clist.index(ucategory) + 1:len(clist)]
        maxvalue = pd.concat([condition1, condition2]).max()

        temp_v = pd.concat([condition1, condition2]) == maxvalue
        temp_list = pd.concat([condition1, condition2])[temp_v].index.tolist()

        # 이번달& 지난달 최대 지출 날짜

        today = datetime.today()
        before_one_month = today - relativedelta(months=1)
        months_ago = before_one_month.strftime("%Y-%m")

        time = datetime.today().strftime("%Y-%m")
        dataFilter = df['date'].str.contains(time)
        result_thismonth = df[dataFilter]
        dataFilter = df['date'].str.contains(months_ago)
        result_lastmonth = df[dataFilter]

        u_lastmonth = result_lastmonth['name'] == uid
        u_thismonth = result_thismonth['name'] == uid

        lastmonth_list = result_lastmonth[u_lastmonth]['date'].unique().tolist()
        thismonth_list = result_thismonth[u_thismonth]['date'].unique().tolist()

        if len(lastmonth_list) == 0 and len(thismonth_list) == 0:
            print(lastmonth_list)
            print(thismonth_list)

        if len(lastmonth_list) != 0 and len(thismonth_list) != 0:
            lastmonth_result = result_lastmonth[u_lastmonth]
            thismonth_result = result_thismonth[u_thismonth]

            lastmonth_cost_list = []
            thismonth_cost_list = []
            for i in range(len(lastmonth_list)):
                lastmonth_cost_list.append(
                    lastmonth_result[result_lastmonth[u_lastmonth]['date'] == lastmonth_list[i]]['cost'].sum())

            for i in range(len(thismonth_list)):
                thismonth_cost_list.append(
                    thismonth_result[result_thismonth[u_thismonth]['date'] == thismonth_list[i]]['cost'].sum())

            lastmonth_max_index = [index for index, item in enumerate(lastmonth_cost_list) if
                                   item == max(thismonth_cost_list)]
            thismonth_max_index = [index for index, item in enumerate(thismonth_cost_list) if
                                   item == max(thismonth_cost_list)]

            if len(lastmonth_max_index) == 0:
                lastmonth_max_index = (lastmonth_cost_list.index(max(lastmonth_cost_list)))

            if len(thismonth_max_index) == 0:
                thismonth_max_index = (thismonth_cost_list.index(max(thismonth_cost_list)))

            if isinstance(lastmonth_max_index, list) == False:
                max_index = []
                max_index.append(lastmonth_max_index)
                lastmonth_max_index = max_index

            if isinstance(thismonth_max_index, list) == False:
                max_index = []
                max_index.append(thismonth_max_index)
                thismonth_max_index = max_index

            lastmonth_result = []
            thismonth_result = []

            for i in range(len(lastmonth_max_index)):
                lastmonth_result.append(lastmonth_list[lastmonth_max_index[i]])

            for i in range(len(thismonth_max_index)):
                thismonth_result.append(thismonth_list[thismonth_max_index[i]])

            lastmonth_list.clear()
            lastmonth_list = lastmonth_result

            thismonth_list.clear()
            thismonth_list = thismonth_result

        #카테고리별 지출 top3

        my_df = df['name'] == uid
        print(my_df)
        dict_data = df[my_df]['category'].value_counts(ascending=False)
        dict_data = pd.Series(dict_data)
        category_unique = (df[my_df]['category'].value_counts(ascending=False).unique())

        if len(dict_data.index) >= 3:
            for i in range(3):
                print(dict_data.index[i])
        else:
            for i in range(len(dict_data.index)):
                print(dict_data.index[i])

        category_freq = pd.DataFrame()
        category_freq['category'] = dict_data.index
        category_freq['count'] = dict_data.values

        print(category_freq)

        cate = []

        if len(category_unique) < 3:
            for i in range(len(category_unique)):
                cate.extend(str(i + 1) + "위" +category_freq['category'][category_freq['count'] == category_unique[i]])
        else :
            for i in range(3):
                cate.extend(str(i + 1) + "위" +category_freq['category'][category_freq['count'] == category_unique[i]])

        return category_frequency, users_lastmonth_freq, users_average_consum, u_lastmonth_freq, u_average_consum, lastmonth_list, thismonth_list, cate, temp_list