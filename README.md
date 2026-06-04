# Omni-Quant

**End-to-end MLOps platform for cryptocurrency price forecasting.**

Omni-Quant is a production-grade system that trains multiple models (XGBoost, LightGBM, LSTM, Auto-ARIMA) on live CoinGecko market data, backtests them with walk-forward validation, logs experiments to MLflow with SHAP explainability, and serves predictions through a Flask web UI — all orchestrated asynchronously with Celery.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Browser    │────►│   Flask      │────►│   Celery Worker  │
│  (index.js)  │     │   app.py     │     │   ml/tasks.py    │
└──────────────┘     └──────┬───────┘     └────────┬─────────┘
       ▲                      │                     │
       │              ┌───────┴───────┐     ┌───────┴─────────┐
       │              │   /api/*      │     │  Feature Engineering
       │              │   endpoints   │     │  + Backtesting
       │              └───────────────┘     │  + Model Training
       │                                    │  + MLflow Logging
       │                                    └────────┬─────────┘
       │                                             │
       └─────────────────────────────────────────────┘
                          JSON response
```

## Pipeline

```
User clicks "Forecast"
        │
        ▼
Flask POST /predict ──────────► Returns task_id (202 Accepted)
        │
        ▼
Celery worker picks up task
        │
        ├── 1. Fetch 120d market data (CoinGecko API)
        ├── 2. Feature engineering (15+ indicators)
        ├── 3. Walk-forward backtest (each model)
        ├── 4. Train on full dataset
        ├── 5. Log experiment to MLflow (params, metrics, SHAP plots)
        └── 6. Return predictions + metrics
        │
        ▼
Browser polls GET /task/:id ──► Renders result
```

## Technology Stack

| Layer | Technology |
|---|---|
| **Web UI** | Flask, Jinja2, HTML5 Canvas, CSS3 |
| **API** | Flask REST endpoints |
| **Task Queue** | Celery + Redis (broker/backend) |
| **Machine Learning** | XGBoost, LightGBM, TensorFlow/Keras (LSTM), scikit-learn |
| **Time Series** | pmdarima (Auto-ARIMA), arch (GARCH) |
| **Feature Engineering** | pandas, numpy, ta (Technical Analysis library) |
| **MLOps** | MLflow (tracking + registry), SHAP (explainability) |
| **Database** | PostgreSQL (SQLAlchemy ORM), falls back to SQLite |
| **Containerization** | Docker, Docker Compose |
| **Deployment** | Render.com (render.yaml) |
| **Monitoring** | Flower (Celery dashboard) |

## Project Structure

```
omni-quant/
├── app.py                          Flask application, routes, API endpoints
├── celery_app.py                   Celery configuration + scheduled beats
├── docker-compose.yml              7-service stack (web, worker, redis, db, mlflow, beat, flower)
├── Dockerfile                      Python 3.11-slim base
├── render.yaml                     Render.com deployment blueprint
├── requirements.txt                Python dependencies
├── .gitignore
├── .dockerignore
├── LICENSE                         MIT
├── README.md
│
├── ml/
│   ├── tasks.py                    Celery task: full MLOps pipeline orchestration
│   ├── features.py                 Feature engineering (RSI, MACD, Bollinger Bands, etc.)
│   ├── backtest.py                 Walk-forward validation engine + metrics
│   ├── forecaster.py               Auto-ARIMA + GARCH(1,1) volatility models
│   ├── experiment_tracking.py      MLflow + SHAP logging wrapper
│   ├── __init__.py
│   └── models/
│       ├── xgboost_model.py        XGBoost forecaster (sklearn interface)
│       ├── lightgbm_model.py       LightGBM forecaster (sklearn interface)
│       └── lstm_model.py           LSTM forecaster (TensorFlow/Keras)
│
├── services/
│   ├── coingecko_api.py            CoinGecko API client with 10-min cache
│   ├── database.py                 SQLAlchemy models (Price, ModelVersion, Experiment, Forecast)
│   └── __init__.py
│
├── templates/
│   ├── index.html                  Landing page: coin selector + prediction UI
│   ├── graph.html                  Market trends chart page
│   ├── dashboard.html              Model comparison dashboard (live metrics table)
│   └── predict.html                Placeholder
│
└── static/
    ├── scripts/
    │   ├── index.js                 Main page JS: polling, prediction, navigation
    │   └── grp.js                   Chart page JS: Canvas charting, coin switching
    └── styles/
        ├── style.css                Global glassmorphism design system
        └── grp.css                  Chart page extensions
```

## Models

Each model is wrapped in a scikit-learn-compatible interface (`BaseEstimator`, `RegressorMixin`) so they share a common `.fit(X, y)` / `.predict(X)` API.

### XGBoost

```python
ml/models/xgboost_model.py
```

- `XGBRegressor` with `reg:squarederror` objective
- Configurable: `n_estimators`, `max_depth`, `learning_rate`
- SHAP `TreeExplainer` for feature importance

### LightGBM

```python
ml/models/lightgbm_model.py
```

- `LGBMRegressor` with leaf-wise tree growth
- Configurable: `n_estimators`, `num_leaves`, `learning_rate`
- SHAP `TreeExplainer` for feature importance

### LSTM

```python
ml/models/lstm_model.py
```

- TensorFlow/Keras `Sequential` model: LSTM → Dropout → Dense
- Configurable: `time_steps`, `units`, `epochs`, `batch_size`, `learning_rate`
- Handles sequence creation internally via sliding window
- Falls back to a dummy predictor when data is too short for the time window

### Auto-ARIMA

```python
ml/forecaster.py :: predict_with_auto_arima()
```

- `pmdarima.auto_arima` dynamically selects best (p, d, q)
- Returns prediction + 95% confidence interval
- Model metadata: AIC, selected order

### GARCH(1,1)

```python
ml/forecaster.py :: predict_volatility()
```

- `arch_model` with GARCH(1,1) for volatility forecasting
- Models return variance → converts to volatility (standard deviation)

## Feature Engineering

`ml/features.py` transforms raw CoinGecko price/volume data into a DataFrame with 15+ features:

| Category | Features |
|---|---|
| **Returns** | `returns`, `log_returns` |
| **Volatility** | `volatility_7d`, `volatility_30d` (rolling std annualized) |
| **Momentum** | `rsi_14` (Relative Strength Index) |
| **Trend** | `macd`, `macd_signal`, `macd_diff` (MACD), `sma_7`, `sma_30`, `ema_7` |
| **Volatility** | `bb_high`, `bb_low`, `bb_mavg`, `bb_width` (Bollinger Bands) |
| **Volume** | `volume_sma_7`, `volume_change` |

## Walk-Forward Validation

`ml/backtest.py` implements a strict time-series backtesting engine:

```
Train [----------------] Test [----]
      Train [------------------] Test [----]
            Train [--------------------] Test [----]
```

- `initial_train_size`: 30 days
- `test_size`: 7 days per window
- Slides forward in weekly increments
- Metrics computed: **RMSE**, **MAE**, **MAPE**, **Directional Accuracy**, **Simulated Sharpe Ratio**

Directional accuracy measures how often the model correctly predicts whether price will go up or down. The simulated Sharpe ratio is computed from a simple long/short strategy based on predicted direction.

## MLflow Experiment Tracking

Each model run logs to MLflow (`http://localhost:5001`):

- **Parameters**: model hyperparameters (n_estimators, max_depth, etc.)
- **Metrics**: RMSE, MAE, MAPE, Directional Accuracy, Sharpe Ratio
- **Artifacts**: SHAP feature importance bar plots (XGBoost, LightGBM)
- **Model Registry**: models saved via `mlflow.xgboost.log_model()`, `mlflow.lightgbm.log_model()`, etc.

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Main UI |
| `GET` | `/graph.html` | Market trends chart |
| `GET` | `/dashboard` | Model comparison dashboard |
| `GET` | `/api/market-data/<coin_id>` | Raw price/volume data |
| `POST` | `/api/train` | Trigger ML pipeline (alias for predict) |
| `POST` | `/api/forecast` | Trigger ML pipeline |
| `POST` | `/api/backtest` | Trigger ML pipeline |
| `GET` | `/api/models` | Model registry listing |
| `GET` | `/api/metrics` | Latest experiment metrics from DB |
| `POST` | `/predict` | Start prediction task (returns task_id) |
| `GET` | `/task/<task_id>` | Poll Celery task status/result |

## Getting Started

### Docker (recommended)

```bash
docker-compose up --build
```

Starts 7 services:

| Service | Port | Purpose |
|---|---|---|
| `web` | `5000` | Flask application (Gunicorn) |
| `worker` | — | Celery task worker |
| `redis` | `6379` | Message broker / result backend |
| `db` | `5432` | PostgreSQL |
| `mlflow` | `5001` | MLflow tracking server |
| `beat` | — | Celery beat (scheduled retraining) |
| `flower` | `5555` | Celery monitoring dashboard |

### Access

| URL | What |
|---|---|
| `http://localhost:5000` | Main UI — select coin, forecast, view trends |
| `http://localhost:5000/dashboard` | Model comparison table |
| `http://localhost:5001` | MLflow UI — experiments, params, SHAP plots |
| `http://localhost:5555` | Flower — Celery task monitoring |

### Scheduled Retraining

Celery Beat runs `compute_predictions('bitcoin', 1)` daily at midnight (`celery_app.py`).

## Frontend

### Design

Glassmorphism theme with animated gradient background, neon accents (`#6366f1` / `#ec4899`), and smooth transitions. Responsive layout.

### Pages

- **`/`** — Coin selector dropdown (BTC, ETH, SOL, DOGE, BNB), "Get Prediction" reveals input panel, "View Trends" navigates to chart page with coin preselected. Polls Celery task status every 2 seconds and renders the ARIMA price prediction.
- **`/graph.html`** — Native HTML5 Canvas line chart with gradient fill, neon glow stroke, price grid, and responsive redraw. Coin selector swaps chart data live. Same prediction panel available.
- **`/dashboard`** — Table of walk-forward metrics loaded from `/api/metrics`. Directional Accuracy > 50% and Sharpe > 1.0 highlighted in green.

### Charts

Charting is done with raw Canvas 2D API (no library dependency). Features gradient area fill, neon glow shadow, grid lines, auto-scaled Y axis, and debounced window resize handler.

## Database Schema

`services/database.py` defines 4 SQLAlchemy models:

| Table | Columns | Purpose |
|---|---|---|
| `prices` | id, coin_id, timestamp, price | Historical price records |
| `model_versions` | id, algorithm, parameters (JSON), created_at | Model registry |
| `experiments` | id, arima_version_id, garch_version_id, training_start, training_end, execution_time_ms, metrics (JSON), created_at | Experiment tracking |
| `forecasts` | id, coin_id, experiment_id, predicted_date, predicted_price, lower_bound, upper_bound, volatility, created_at | Prediction storage |

## Deployment

`render.yaml` provides a blueprint for Render.com:

- **Redis** — internal-only, free tier
- **Web service** — Gunicorn, connects to Redis + SQLite fallback
- **Worker** — Celery worker, same environment

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Redis result backend |
| `DATABASE_URL` | `sqlite:///omniquant.db` | PostgreSQL or SQLite |
| `MLFLOW_TRACKING_URI` | `http://mlflow:5001` | MLflow server address |

## CoinGecko API

`services/coingecko_api.py` fetches historical market data with a simple in-memory cache (10-minute TTL) to avoid rate limiting. Supports any CoinGecko coin ID.

## Error Handling

- Flask endpoints return 4xx/5xx with JSON error messages
- Celery tasks capture exceptions and surface them via `task.state === 'FAILURE'`
- Feature engineering drops NaN rows silently
- Walk-forward validation raises on insufficient data
- LSTM model falls back to mean predictor when data is too short
- Database operations use manual `SessionLocal()` management with `finally` cleanup

## Development

```bash
# Local virtualenv (no Docker)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Requires Redis + PostgreSQL running locally
python app.py
```

Note: local mode skips Celery — tasks run synchronously if no Redis is available.

## License

MIT
