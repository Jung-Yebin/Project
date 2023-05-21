import pyrebase
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


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

    def get_user(self, uid):
        list = []
        date = self.db.child("Calendar").child(uid).get()
        for k2, v2 in date.val().items():
            list.append(k2)
            list.append(v2)

        return list

    def budget(self, uid):
        budget_list = []
        budget = self.db.child("User").child(uid).get()

        for k, v in budget.val().items():
            if k == "budget":
                budget_list.append(v)
        return budget_list

    def present_usage(self, uid):
        usage_list = []
        date = self.db.child("Calendar").child(uid).get()
        for k, v in date.val().items():

            for i in range(len(self.db.child("Calendar").child(uid).child().get().val())):
                category = self.db.child("Calendar").child(uid).child(k).get()

            for k2, v2 in category.val().items():
                if None in v2:
                    v2 = {'1': v2[-1]}

                for j in range(len(self.db.child("Calendar").child(uid).child(k).child().get().val())):
                    num = v2

                for k3, v3 in num.items():

                    for n in range(len(k3)):
                        cost = v3

                        for k4, v4 in cost.items():
                            usage_list.append(v4)

        usage_list = list(map(int, usage_list))
        usage_list = sum(usage_list)
        # usage_list = list(map(string, usage_list))
        return usage_list

    def predict_usage(self, uid):
        usage_list = []
        name_list = []
        date = self.db.child("Calendar").child(uid).get()
        for k, v in date.val().items():

            for i in range(len(self.db.child("Calendar").child(uid).child().get().val())):
                category = self.db.child("Calendar").child(uid).child(k).get()

            for k2, v2 in category.val().items():
                if None in v2:
                    v2 = {'1': v2[-1]}

                for j in range(len(self.db.child("Calendar").child(uid).child(k).child().get().val())):
                    num = v2

                for k3, v3 in num.items():

                    for n in range(len(k3)):
                        cost = v3

                        for k4, v4 in cost.items():
                            usage_list.append(v4)
                            name_list.append(uid)

        usage_list = list(map(int, usage_list))
        # usage_list = sum(usage_list)
        # usage_list = list(map(string, usage_list))

        result = pd.DataFrame()

        result['name'] = name_list
        result['cost'] = usage_list

        result.loc[result['name'] == uid, 'name'] = 1

        # print(result)

        x = result[['name']]
        y = result[['cost']]

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=10)
        model = LinearRegression()
        model.fit(x_train, y_train)
        y_predict = model.predict(x_test)

        mse = mean_squared_error(y_test, y_predict)
        mse ** 0.5
        y_predict = y_predict[0]
        return (y_predict)