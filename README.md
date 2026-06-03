# Omni-Quant Advanced MLOps Platform

Omni-Quant is a production-grade, end-to-end Machine Learning Operations (MLOps) platform designed to forecast cryptocurrency prices and volatility using state-of-the-art algorithms and strict statistical backtesting.

## Architecture Highlights

- **Multiple Models:** Object-oriented implementations of XGBoost, LightGBM, LSTM (TensorFlow/Keras), and Auto-ARIMA.
- **Feature Engineering Pipeline:** 15+ domain-specific statistical features engineered dynamically using Pandas and the `ta` library (RSI, MACD, Bollinger Bands, Moving Averages, Volatility, Log Returns).
- **Walk-Forward Validation Engine:** A strict backtesting engine evaluating models across a sliding time-series window, computing industry-standard metrics: RMSE, MAE, MAPE, Directional Accuracy, and Simulated Sharpe Ratio.
- **Experiment Tracking (MLflow):** Fully automated parameter logging, metric tracking, and model artifact registry powered by a local MLflow tracking server backed by PostgreSQL.
- **Explainability (SHAP):** Native integration with SHAP (SHapley Additive exPlanations) to dynamically generate and log feature importance charts for all tree-based boosting models.
- **Asynchronous Orchestration:** High-performance task offloading using Celery and Redis to train and backtest heavy ML pipelines without blocking the REST API.
- **RESTful API:** Exposes endpoints for training (`/api/train`), forecasting (`/api/forecast`), model registry querying (`/api/models`), and retrieving backtest metrics (`/api/metrics`).

## Technology Stack

- **Data Pipeline:** Pandas, NumPy, TA (Technical Analysis), CoinGecko API
- **Machine Learning:** XGBoost, LightGBM, TensorFlow/Keras (LSTM), Scikit-Learn, Statsmodels (ARIMA/GARCH)
- **MLOps & Explainability:** MLflow, SHAP
- **Web & API:** Flask, Gunicorn
- **Orchestration:** Celery, Redis
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Containerization:** Docker, Docker Compose

## Quickstart (Local Infrastructure)

Because this platform utilizes heavy-duty ML libraries and data pipelines, it is configured to run entirely via Docker Compose.

1. Clone the repository and navigate into the directory.
2. Start the entire MLOps stack (Postgres, Redis, MLflow Server, Web Server, Celery Worker):
   ```bash
   docker-compose up --build
   ```

### Accessing the Platform
- **Main Interface:** `http://localhost:5000`
- **Model Comparison Dashboard:** `http://localhost:5000/dashboard`
- **MLflow Tracking Server:** `http://localhost:5001` (View logged parameters, artifacts, and SHAP plots here!)

## The MLOps Pipeline Flow

1. **Trigger:** A request hits `/api/forecast` via the UI.
2. **Task Queue:** Flask immediately returns a `202 Accepted` and offloads the heavy pipeline to the Celery worker via Redis.
3. **Data & Features:** The worker fetches the last 120 days of market data and passes it through `features.py` to engineer 15 advanced momentum and volatility indicators.
4. **Backtesting & Tracking:** 
   - Each model (XGBoost, LightGBM, LSTM) is instantiated.
   - The Walk-Forward Validation engine tests the model historically, returning strict error metrics.
   - The `experiment_tracking.py` wrapper logs the hyperparameters, metrics, and SHAP feature importance plots to the MLflow server.
5. **Final Forecast:** The models are fit on the full dataset to predict tomorrow's price, and the results are returned to the API.

## Explainability

Understanding *why* a model made a decision is critical. When the XGBoost and LightGBM models finish training, the pipeline automatically passes them into a `shap.TreeExplainer`. This generates a Feature Importance bar chart, illustrating exactly which engineered features (e.g., MACD vs RSI) drove the predictions. These plots are automatically saved as artifacts in the MLflow tracking server.
