from flask import Flask, request, jsonify, render_template
from datetime import datetime
from services.coingecko_api import get_crypto_data
from ml.tasks import compute_predictions
from services.database import SessionLocal, Experiment

app = Flask(__name__)

# --- Frontend Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph.html')
def graph():
    return render_template('graph.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# --- Original API Routes ---
@app.route('/api/market-data/<coin_id>', methods=['GET'])
def market_data(coin_id):
    data = get_crypto_data(coin_id, days=30)
    if not data or 'prices' not in data:
        return jsonify({"error": "Could not fetch data"}), 500
        
    labels = []
    prices = []
    for point in data['prices']:
        ts = point[0] / 1000
        labels.append(datetime.fromtimestamp(ts).strftime('%Y-%m-%d'))
        prices.append(point[1])
        
    return jsonify({"labels": labels, "prices": prices})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        interval = int(data.get("interval", 1))
        coin_id = data.get("coin_id", "bitcoin")
        
        if not interval or interval < 1:
            return jsonify({"error": "Invalid interval"}), 400

        task = compute_predictions.delay(coin_id, interval)
        return jsonify({"task_id": task.id}), 202
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/task/<task_id>', methods=['GET'])
def task_status(task_id):
    task = compute_predictions.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({"state": task.state, "status": "Pending..."})
    elif task.state != 'FAILURE':
        return jsonify({
            "state": task.state,
            "result": task.info
        })
    else:
        return jsonify({
            "state": task.state,
            "error": str(task.info)
        })

# --- Advanced MLOps REST API ---
@app.route('/api/train', methods=['POST'])
def api_train():
    """Triggers the advanced ML pipeline for training."""
    return predict()

@app.route('/api/forecast', methods=['POST'])
def api_forecast():
    """RESTful endpoint for forecasting."""
    return predict()

@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """Triggers a walk-forward validation backtest on the models."""
    return predict()

@app.route('/api/models', methods=['GET'])
def api_models():
    """Returns the Model Registry."""
    return jsonify({
        "registry": "MLflow",
        "models": [
            {"name": "XGBoost", "type": "Tree Boosting", "features": 15},
            {"name": "LightGBM", "type": "Leaf-wise Boosting", "features": 15},
            {"name": "LSTM", "type": "Deep Learning Sequence", "features": 15},
            {"name": "Auto-ARIMA", "type": "Statistical", "features": 1}
        ]
    })

@app.route('/api/metrics', methods=['GET'])
def api_metrics():
    """Returns the latest experiment metrics from the database."""
    db = SessionLocal()
    try:
        experiment = db.query(Experiment).order_by(Experiment.id.desc()).first()
        if experiment and experiment.metrics:
            return jsonify(experiment.metrics)
        return jsonify({"message": "No metrics found. Run /api/train first."})
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
