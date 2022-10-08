# -*- coding: utf-8 -*-
"""PredictiveAnalytic.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HttSTrcSJHjsHiy8TTrhFfza9OXjjRYD

#Muhammad Zhafran Ghaly

**M183X0348**

**M02 | Machine Learning and Front-End**

**Import Libraries**
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
# %matplotlib inline
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV, train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.svm import SVR
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression

"""**Data Collecting**

I used dataset from kaggle, https://www.kaggle.com/datasets/muamkh/ihsgstockdata/code
"""

!pip install -q kaggle

from google.colab import files
files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 /root/.kaggle/kaggle.json

!kaggle datasets download -d muamkh/ihsgstockdata

!unzip 'ihsgstockdata.zip'

df = pd.read_csv('/content/daily/BNII.csv')
df['timestamp'] = pd.to_datetime(df['timestamp']) 
df = df.set_index('timestamp')
print(f"Jumlah Baris = {df.shape[0]}")
df.head(5)

df['high'] = df['high'].astype(float)
df['open'] = df['open'].astype(float)
df['low'] = df['low'].astype(float)
df['close'] = df['close'].astype(float)
df['volume'] = df['volume'].astype(float)

df.info()

"""#Exploratory Data Analysis(EDA)

* Transaction Unique Identifier : Pengenal transaksi unik
* Price : Harga dari rumah
* Date of Transfer : Data pengiriman biaya untuk membeli rumah
* Old/New : Kondisi rumah
* Duration : Lamanya kondisi rumah
* Town/city : Kota asal rumahnya
* District : Distrik
* Country : Tempat asal/Negara
* PDD Category Type : Kategori rumahnya
* Record Status - Monthly File only : Jejak dari status rumah

**Missing Value Check**
"""

df.isnull().sum()

print('Null : ', df.isnull().sum().sum())

"""#Statistic Information

**Variable of Agricultural Dataset**

1. count adalah jumlah sampel pada dataset.
2. mean adalah nilai rata-rata dataset.
3. std adalah standar deviasi.
4. min adalah nilai minimum.
5. 25% adalah kuartil pertama.
6. 50% adalah kuartil kedua.
7. 75% adalah kuartil ketiga.
7. max adalah nilai maksimum
"""

df.describe()

"""#Data Visualization

**This is the highest price from 2004 to 2020**
"""

plt.figure(figsize=(15,5))
sns.set_style('darkgrid')
plt.plot(df.index, df['high'])
plt.title("Harga Saham\nBank BNI(BBNI)", fontsize=25)
plt.show()

"""**Overcoming outliner**"""

numerical_col = [col for col in df.columns if df[col].dtypes == 'float64']
plt.subplots(figsize=(10,7))
sns.boxplot(data=df[numerical_col]).set_title("Home Price")
plt.show()

"""By deleting data that is outside the IQR"""

Q1 = df.quantile(0.25)
Q3 = df.quantile(0.75)
IQR = Q3-Q1
df=df[~((df<(Q1-1.5*IQR))|(df>(Q3+1.5*IQR))).any(axis=1)]

df.shape

numerical_col = [col for col in df.columns if df[col].dtypes == 'float64']
plt.subplots(figsize=(10,7))
sns.boxplot(data=df[numerical_col]).set_title("BBNI Price")
plt.show()

"""#Unvariate Analysis"""

cols = 3
rows = 2
fig = plt.figure(figsize=(cols * 5, rows * 5))

for i, col in enumerate(numerical_col):
  ax = fig.add_subplot(rows, cols, i + 1)
  sns.histplot(x=df[col], bins=30, kde=True, ax=ax)
fig.tight_layout()
plt.show()

"""#Multivariate Analysis"""

sns.pairplot(df[numerical_col], diag_kind='kde')
plt.show()

"""**Heatmap Correlation**"""

plt.figure(figsize=(10, 10))
sns.heatmap(df[df.corr().index].corr(), annot = True, cmap = 'inferno')
plt.show()

"""Delete volume column"""

df2 = df.drop(['volume'], axis=1)
df2.head()

"""#Splitting Data"""

X = df2.iloc[:, :-1].values
y = df2.iloc[:, -1].values

X_train, X_test, y_train, y_test = train_test_split(
                                  X, y, test_size=.2,
                                  random_state=42)

print('X_train :', len(X_train))
print('y_train :', len(y_train))
print('X_test  :', len(X_test))
print('y_test  :', len(y_test))

"""**Normalization**

Using Minmaxscaler() to speed up training of our data
"""

scal = MinMaxScaler()
X_train = scal.fit_transform(X_train)
X_test = scal.transform(X_test)

models = pd.DataFrame(columns=['train_mse', 'test_mse'], index=['SVR', 'KNN', 'GradientBoosting'])

"""#Modeling

**Hyperparameter Tuning** is choosing a set of optimal hyperparameters for a learning algorithm
"""

def grid_search(model, hyperparameters):
  results = GridSearchCV(
      model,
      hyperparameters,
      cv=5,
      verbose=1,
      n_jobs=6
  )

  return results

svr = SVR()
hyperparameters = {
    'kernel': ['rbf'],
    'C': [0.001, 0.01, 0.1, 10, 100, 1000],
    'gamma': [0.3, 0.03, 0.003, 0.0003]
}

svr_search = grid_search(svr, hyperparameters)
svr_search.fit(X_train, y_train)
print(svr_search.best_params_)
print(svr_search.best_score_)

gradient_boost = GradientBoostingRegressor()
hyperparameters = {
    'learning_rate': [0.01, 0.001, 0.0001],
    'n_estimators': [250, 500, 750, 1000],
    'criterion': ['friedman_mse', 'squared_error']
}

gradient_boost_search = grid_search(gradient_boost, hyperparameters)
gradient_boost_search.fit(X_train, y_train)
print(gradient_boost_search.best_params_)
print(gradient_boost_search.best_score_)

knn = KNeighborsRegressor()
hyperparameters = {
    'n_neighbors': range(1, 10)
}

knn_search = grid_search(knn, hyperparameters)
knn_search.fit(X_train, y_train)
print(knn_search.best_params_)
print(knn_search.best_score_)

"""#Training Model"""

svr = SVR(C=1000, gamma=0.003, kernel='rbf')
svr.fit(X_train, y_train)

gradient_boost = GradientBoostingRegressor(criterion='squared_error',
                                           learning_rate=0.01, n_estimators=1000)
gradient_boost.fit(X_train, y_train)

knn = KNeighborsRegressor(n_neighbors=6)
knn.fit(X_train, y_train)

"""#Evaluation Model"""

model_dict = {
    'SVR': svr,
    'KNN': knn,
    'GradientBoosting': gradient_boost,
    
}

for name, model in model_dict.items():
  models.loc[name, 'train_mse'] = mean_squared_error(y_train, model.predict(X_train))
  models.loc[name, 'test_mse'] = mean_squared_error(y_test, model.predict(X_test))

models.head()

models.sort_values(by='test_mse', ascending=False).plot(kind='bar', zorder=3)

svr_acc = svr.score(X_test, y_test)*100
knn_acc = knn.score(X_test, y_test)*100
boosting_acc = gradient_boost.score(X_test, y_test)*100

"""**From the evaluation results below, it can provide information that the third model built has a performance above 99%. It can be seen that the model with the Gradient Boost algorithm has a performance measured by a better accuracy value than the other two models, namely the model with the SVR and KNN algorithms.**"""

evaluation_list = [[svr_acc], [knn_acc], [boosting_acc]]
evaluation = pd.DataFrame(evaluation_list,
                          columns = ['Accuracy (%)'],
                          index = ['SVR', 'KNN', 'Gradient Boost'])

evaluation

X_30=X[-30:]
forecast=gradient_boost.predict(X_30)

forecast=pd.DataFrame(forecast,columns=['Forecast'])
bbni = df2.append(forecast)
bbni.drop(['high', 'low', 'open'],axis=1,inplace=True)

"""**The following is the predicted value for the next 30 days obtained from the best method, namely the previously prospective Gradient Boost**"""

bbni.tail(35)