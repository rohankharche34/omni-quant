import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class LSTMForecaster(BaseEstimator, RegressorMixin):
    def __init__(self, time_steps=7, units=50, epochs=10, batch_size=16, learning_rate=0.001):
        self.time_steps = time_steps
        self.units = units
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.model = None

    def _create_sequences(self, X, y=None):
        Xs, ys = [], []
        X_val = X.values if hasattr(X, 'values') else X
        y_val = y.values if hasattr(y, 'values') else y if y is not None else None
        
        for i in range(len(X_val) - self.time_steps):
            Xs.append(X_val[i:(i + self.time_steps)])
            if y_val is not None:
                ys.append(y_val[i + self.time_steps])
        
        if y_val is not None:
            return np.array(Xs), np.array(ys)
        return np.array(Xs)

    def _build_model(self, input_shape):
        model = Sequential([
            LSTM(self.units, activation='relu', input_shape=input_shape, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        model.compile(optimizer=optimizer, loss='mse')
        return model

    def fit(self, X, y):
        if len(X) <= self.time_steps:
             self.model = "dummy"
             self.last_y = np.mean(y)
             return self
             
        X_seq, y_seq = self._create_sequences(X, y)
        if len(X_seq) == 0:
             self.model = "dummy"
             self.last_y = np.mean(y)
             return self
             
        self.model = self._build_model((X_seq.shape[1], X_seq.shape[2]))
        
        self.model.fit(
            X_seq, y_seq,
            epochs=self.epochs,
            batch_size=self.batch_size,
            verbose=0
        )
        return self

    def predict(self, X):
        if self.model == "dummy":
             return np.full(len(X), self.last_y)
             
        X_val = X.values if hasattr(X, 'values') else X
        if len(X_val) < self.time_steps:
            pad = np.tile(X_val[0], (self.time_steps - len(X_val), 1))
            X_val = np.vstack([pad, X_val])
            
        X_seq = self._create_sequences(X_val)
        
        if len(X_seq) == 0:
             return np.full(len(X), np.nan)
             
        preds = self.model.predict(X_seq, verbose=0)
        
        pad_preds = np.full(self.time_steps, preds[0][0])
        return np.concatenate([pad_preds, preds.flatten()])
        
    def get_params(self, deep=True):
        return {
            "time_steps": self.time_steps,
            "units": self.units,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate
        }
