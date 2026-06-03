# Omni-Quant 🧠 📈

**Omni-Quant** is a professional, high-performance cryptocurrency forecasting platform built for speed and precision. 
By combining a distributed asynchronous architecture (Flask + Celery + Redis) with mathematically rigorous statistical models (Auto-ARIMA and GARCH), Omni-Quant is Designed for robust short-term forecasting and volatility estimation using statistical time-series methods for major cryptocurrencies.

This project was specifically designed to balance complex research methodologies with robust, production-ready software engineering principles, serving as a powerful resume piece.

## 🌟 Key Features

- **Blazing Fast Statistical Models**: Powered by `pmdarima` for automated ARIMA (Auto-Regressive Integrated Moving Average) modeling, instantly identifying the optimal parameters for time-series forecasting.
- **Asynchronous Architecture**: Employs `Celery` workers and a `Redis` message broker to offload heavy mathematical computations, ensuring the frontend remains completely non-blocking and highly responsive.
- **Native HTML5 Canvas Graph**: Features a completely custom, dependency-free `<canvas>` rendering engine that draws beautiful, neon-glowing charts without relying on unreliable 3rd-party CDN libraries (like TradingView or Chart.js).
- **Multi-Cryptocurrency Support**: Seamlessly analyzes historical data and generates predictions for Bitcoin, Ethereum, Solana, Dogecoin, and Binance Coin via the real-time CoinGecko API.
- **Ultra-Lightweight Dockerization**: The entire distributed architecture (Web Server, Celery Workers, and Redis) is heavily optimized and containerized using Docker Compose, booting from scratch in under 2 minutes.

---

## 🏗️ Technical Architecture

1. **Frontend**: HTML5, Vanilla CSS (Glassmorphism design), Vanilla JS, Custom Native Canvas API.
2. **Backend**: Python, Flask, SQLAlchemy.
3. **Task Queue**: Celery.
4. **Message Broker**: Redis (Alpine Container).
5. **Machine Learning / Statistics**: `pmdarima` (Auto-ARIMA), `arch` (GARCH Volatility), `pandas`, `statsmodels`.

---

## 🚀 Quick Start (Docker)

The absolute best way to run Omni-Quant is using Docker. The environment is heavily optimized, and thanks to a strict `.dockerignore`, the image size is incredibly lightweight (~300MB).

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed and running.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Run the System
Navigate to the root directory of the project and run:

```bash
docker compose build
docker compose up -d
```

That's it! Docker will automatically pull the Redis Alpine image, build the Python Web and Worker containers, and link them on an internal network.
- The web app will be available at: **http://localhost:5000**
- You can monitor the backend workers by running: `docker compose logs -f worker`

---

## 💻 Local Development (Without Docker)

If you prefer to run the system directly on your host machine for development or debugging, follow these steps:

### 1. Start Redis
You must have a Redis server running locally. The easiest way is via Docker:
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Start the Celery Worker
In one terminal (with the virtual environment activated), start the background worker:
```bash
python -m celery -A celery_app.celery worker --loglevel=info
```

### 4. Start the Flask Server
In a separate terminal (with the virtual environment activated), start the web application:
```bash
python app.py
```
The site will be running at `http://127.0.0.1:5000`.

---

## 📊 How the Forecasting Works

Omni-Quant uses the **Auto-ARIMA** algorithm to predict future cryptocurrency prices.
Unlike standard Machine Learning models (like LSTMs) which require massive datasets and long training times (often resulting in overfitting on noisy financial data), ARIMA is a classic statistical model that analyzes the *autocorrelation* in the time series.

When a user clicks "Forecast", the following occurs:
1. The frontend polls the backend and initiates an asynchronous **Celery task**.
2. The Celery worker fetches the last 90 days of closing prices from the CoinGecko API.
3. The Auto-ARIMA algorithm performs a grid-search (minimizing the Akaike Information Criterion / AIC score) to find the absolute best `(p, d, q)` parameters for the specific coin's current market behavior.
4. The model fits the data and generates a prediction for the requested number of future days.
5. The frontend safely polls the task ID until the worker marks it as `SUCCESS`, seamlessly updating the UI with the final result.

---

## 🛡️ License
This project is licensed under the MIT License.
