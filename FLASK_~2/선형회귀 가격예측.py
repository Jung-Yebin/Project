from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd

data= {
    'category' : ['문구류', '교통비', '여가비', '식비', '식비', '식비', '식비', '식비', '식비', '식비', '식비', '식비'],
    'cost' : [10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000],
}
#'cost': [10000, 20000, 10000, 40000, 100000, 200000, 50000, 35000, 5000, 3500, 15000, 150000],
df = pd.DataFrame(data)

df.loc[df['category'] == '문구류', 'category'] = 1
df.loc[df['category'] == '교통비','category'] = 2
df.loc[df['category'] == '여가비','category'] = 3
df.loc[df['category'] == '식비','category'] = 4

x = df[['category']]
y = df[['cost']]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=10)
model = LinearRegression()
model.fit(x_train, y_train)
y_predict = model.predict(x_test)

mse = mean_squared_error(y_test, y_predict)
mse ** 0.5

print(y_predict[0])