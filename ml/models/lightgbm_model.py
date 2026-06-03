import lightgbm as lgb
from sklearn.base import BaseEstimator, RegressorMixin

class LightGBMForecaster(BaseEstimator, RegressorMixin):
    def __init__(self, n_estimators=100, num_leaves=31, learning_rate=0.1, random_state=42):
        self.n_estimators = n_estimators
        self.num_leaves = num_leaves
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model = lgb.LGBMRegressor(
            n_estimators=self.n_estimators,
            num_leaves=self.num_leaves,
            learning_rate=self.learning_rate,
            random_state=self.random_state
        )

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict(self, X):
        return self.model.predict(X)
        
    def get_params(self, deep=True):
        return {
            "n_estimators": self.n_estimators,
            "num_leaves": self.num_leaves,
            "learning_rate": self.learning_rate,
            "random_state": self.random_state
        }
