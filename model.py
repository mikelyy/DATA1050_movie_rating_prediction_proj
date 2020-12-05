from tensorflow import keras
from preprocessing import *
import gensim
from web_core import *
from language_processing import *
from sklearn import preprocessing as pp
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.tree import ExtraTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
import xgboost as xgb
from sklearn.model_selection import train_test_split
import numpy as np


# An example:
searcher = WebSearch()  # Initializing the searching engine
dkn = searcher.search('dark knight', pl=200)  # Scraping the data from movie "the dark knight"
reviews = list(dkn.values())[0][13]  # Extracting the reviews
scores = [int(x[0]) for x in reviews]  # Extracting the scores as training label
text = [x[1] for x in reviews]
pr = ProcessR(text)

x_train, y_train = np.array(pr.doc_vs), np.array(scores).astype(float)

for i in [3,4,5,6,7,8,9,10,11,12,15,20,30,40,50,70]:
    knn = KNeighborsRegressor(n_neighbors=i)
    knn.fit(x_train, y_train)

rfr = RandomForestRegressor()
rfr.fit(x_train, y_train)
np.mean(abs(rfr.predict(x_test) - y_test))
# lbl = pp.LabelEncoder()
# y_train_xgb = lbl.fit_transform(y_train)
# y_test_xgb = lbl.fit_transform(y_test)
dtrain = xgb.DMatrix(x_train, y_train)
dtest = xgb.DMatrix(x_test, y_test)
param = {'max_depth': 60, 'eta': 0.03, 'objective': 'reg:squarederror',
         'booster': 'gbtree'}
evallist = [(dtrain, 'train')]
model = xgb.train(param, dtrain, 300, evallist)  # Train a xgboost model (regression task)


# Test with an example
test_example = 'i really enjoy watching the film with my girlfriend, although she is a little frightened. in all, I am very satisfy with the film, especially the joker! Really cool!'
te_vec = pr.infer(pr.process_text(test_example))
knn.predict(np.reshape(te_vec, (1, -1)))