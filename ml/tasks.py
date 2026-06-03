from celery_app import celery
from ml.forecaster import predict_with_auto_arima, predict_volatility
from services.coingecko_api import get_crypto_data
from services.database import SessionLocal, Price, ModelVersion, Experiment, Forecast
import datetime
import time
import pandas as pd

from ml.features import build_features
from ml.backtest import walk_forward_validation
from ml.models.xgboost_model import XGBoostForecaster
from ml.models.lightgbm_model import LightGBMForecaster
from ml.models.lstm_model import LSTMForecaster
from ml.experiment_tracking import log_experiment

@celery.task
def compute_predictions(coin_id, interval):
    """
    Background task that runs the full advanced MLOps pipeline.
    """
    db = SessionLocal()
    try:
        # 1. Fetch data
        market_info = get_crypto_data(coin_id, days=120) # Fetch more for feature engineering window
        if not market_info or 'prices' not in market_info:
            return {"error": "Could not fetch data for prediction"}
        
        # 2. Build Advanced Features
        df = build_features(market_info)
        if len(df) < 30:
            return {"error": "Not enough historical data after feature engineering."}

        # Features to use for modeling
        feature_cols = [c for c in df.columns if c not in ['timestamp', 'close']]
        
        # We will train on all available data for the final forecast
        X_full = df[feature_cols]
        y_full = df['close']
        
        predictions_out = {}
        experiment_metrics = {}

        # 3. XGBoost Pipeline
        xgb = XGBoostForecaster()
        xgb_metrics = walk_forward_validation(XGBoostForecaster, df, feature_cols)
        xgb.fit(X_full, y_full)
        # Predict next day: use last row of features
        xgb_pred = float(xgb.predict(X_full.iloc[[-1]])[0])
        log_experiment("XGBoost", xgb, xgb.get_params(), xgb_metrics, X_full)
        predictions_out["xgboost"] = xgb_pred
        experiment_metrics["xgboost"] = xgb_metrics

        # 4. LightGBM Pipeline
        lgb = LightGBMForecaster()
        lgb_metrics = walk_forward_validation(LightGBMForecaster, df, feature_cols)
        lgb.fit(X_full, y_full)
        lgb_pred = float(lgb.predict(X_full.iloc[[-1]])[0])
        log_experiment("LightGBM", lgb, lgb.get_params(), lgb_metrics, X_full)
        predictions_out["lightgbm"] = lgb_pred
        experiment_metrics["lightgbm"] = lgb_metrics

        # 5. LSTM Pipeline
        lstm = LSTMForecaster(time_steps=7, epochs=10)
        lstm_metrics = walk_forward_validation(LSTMForecaster, df, feature_cols, time_steps=7, epochs=5)
        lstm.fit(X_full, y_full)
        lstm_pred = float(lstm.predict(X_full.iloc[-7:])[0]) # Predict on last window
        log_experiment("LSTM", lstm, lstm.get_params(), lstm_metrics, X_full)
        predictions_out["lstm"] = lstm_pred
        experiment_metrics["lstm"] = lstm_metrics

        # 6. Legacy ARIMA & GARCH (for comparison)
        prices_list = df['close'].tolist()
        arima_results = predict_with_auto_arima(prices_list, interval)
        garch_results = predict_volatility(prices_list, interval)
        predictions_out["arima"] = arima_results["prediction"]
        predictions_out["volatility"] = garch_results["volatility"]

        return {
            "coin_id": coin_id,
            "predictions": predictions_out,
            "metrics": experiment_metrics
        }

    except Exception as e:
        db.rollback()
        print(f"Pipeline Error: {e}")
        raise e
    finally:
        db.close()
