from celery_app import celery
from ml.forecaster import predict_with_auto_arima
from services.coingecko_api import get_crypto_data

@celery.task
def compute_predictions(coin_id, interval):
    """
    Background task that runs Auto-ARIMA.
    """
    market_info = get_crypto_data(coin_id, days=90)
    if not market_info or 'prices' not in market_info:
        return {"error": "Could not fetch data for prediction"}
         
    prices = [p[1] for p in market_info['prices']]
    
    # Run statistical ML model
    arima_results = predict_with_auto_arima(prices, interval)
    
    return {
        "coin_id": coin_id,
        "auto_arima": arima_results
    }
