import pandas as pd
import pyrebase

firebaseConfig = {'apiKey': "AIzaSyBFIpc30kRLllfUs710cbbGZTasFXEYXPk",
    'authDomain': "vita-d7ca1.firebaseapp.com",
    'databaseURL': "https://vita-d7ca1-default-rtdb.firebaseio.com",
    'projectId': "vita-d7ca1",
    'storageBucket': "vita-d7ca1.appspot.com",
    'messagingSenderId': "860961095524",
    'appId': "1:860961095524:web:fdddb042dab3b2d7fec471",
    'measurementId': "G-MRS6WFXE9C"}

firebase=pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

calendar=db.child("Calendar").get()

na=[]
da=[]
cate=[]
items=[]
co=[]

for k,v in calendar.val().items():
    #print(k)
    #na.append(k)

    df1=pd.DataFrame(na)

    for i in range(len(db.child("Calendar").get().val())):
        date=db.child("Calendar").child(k).get()
        #print(date.val())
    for k2,v2 in date.val().items():
        #print(k2)
        #da.append(k2)

        df2=pd.DataFrame(da)

        for j in range(len(db.child("Calendar").child(k).child().get().val())):
            #print(len(db.child("Calendar").child(k).child().get().val()))
            category=db.child("Calendar").child(k).child(k2).get()
            #print(category.val())

        for k3, v3 in category.val().items():
            #print(k3)



            for m in range(len(db.child("Calendar").child(k).child(k2).child(k3).get().val())):
                cost=db.child("Calendar").child(k).child(k2).child(k3).get()

                na.append(k)
                da.append(k2)



            for k4, v4 in cost.val().items():
                #print(k4,v4)
                items.append(k4)
                df4=pd.DataFrame(items)

                new_k3 = (k3.split('&'))
                n_k3 = "".join(new_k3)
                # print(n_k3)
                category = []
                category.append(n_k3)
                cate.extend(category)
                df3 = pd.DataFrame(cate)

                cost=[]
                cost.append(v4)
                co.extend(cost)

                df5 = pd.DataFrame(co)


#print(na)
#print(da)
#print(cate)
#print(items)
#print(co)

result = pd.DataFrame()

result['name'] = na
result['date'] = da
result['category'] = cate
result['items'] = items
result['cost'] = co

print(result)
