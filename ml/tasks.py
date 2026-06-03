from celery_app import celery
from ml.forecaster import predict_with_auto_arima, predict_volatility
from services.coingecko_api import get_crypto_data
from services.database import SessionLocal, Price, ModelVersion, Experiment, Forecast
import datetime
import time

@celery.task
def compute_predictions(coin_id, interval):
    """
    Background task that runs Auto-ARIMA and GARCH, saving all data to Postgres.
    """
    db = SessionLocal()
    try:
        # 1. Fetch data
        market_info = get_crypto_data(coin_id, days=45)
        if not market_info or 'prices' not in market_info:
            return {"error": "Could not fetch data for prediction"}
        
        # 2. Save prices to Postgres
        prices_data = market_info['prices']
        
        latest_price_record = db.query(Price).filter(Price.coin_id == coin_id).order_by(Price.timestamp.desc()).first()
        latest_ts = latest_price_record.timestamp if latest_price_record else datetime.datetime.min
        
        new_prices = []
        for p in prices_data:
            ts = datetime.datetime.fromtimestamp(p[0] / 1000.0)
            if ts > latest_ts:
                new_prices.append(Price(coin_id=coin_id, timestamp=ts, price=p[1]))
        
        if new_prices:
            db.bulk_save_objects(new_prices)
            db.commit()
            
        # 3. Query prices from DB for feature pipeline
        forty_five_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=45)
        db_prices = db.query(Price).filter(Price.coin_id == coin_id, Price.timestamp >= forty_five_days_ago).order_by(Price.timestamp.asc()).all()
        
        if len(db_prices) < 20:
             return {"error": "Not enough historical data in DB to train models."}
             
        prices_list = [p.price for p in db_prices]
        training_start = db_prices[0].timestamp
        training_end = db_prices[-1].timestamp
        
        start_time = time.time()
        
        # 4. Run ML Models
        arima_results = predict_with_auto_arima(prices_list, interval)
        garch_results = predict_volatility(prices_list, interval)
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        # 5. Log Model Versions
        arima_version = ModelVersion(algorithm="ARIMA", parameters=arima_results["parameters"])
        garch_version = ModelVersion(algorithm="GARCH", parameters=garch_results["parameters"])
        db.add(arima_version)
        db.add(garch_version)
        db.commit() 
        
        # 6. Log Experiment
        experiment = Experiment(
            arima_version_id=arima_version.id,
            garch_version_id=garch_version.id,
            training_start=training_start,
            training_end=training_end,
            execution_time_ms=execution_time_ms,
            metrics={"arima_aic": arima_results["metrics"]["aic"], "garch_aic": garch_results["metrics"]["aic"]}
        )
        db.add(experiment)
        db.commit() 
        
        # 7. Log Forecast
        predicted_date = datetime.datetime.utcnow() + datetime.timedelta(days=interval)
        forecast = Forecast(
            coin_id=coin_id,
            experiment_id=experiment.id,
            predicted_date=predicted_date,
            predicted_price=arima_results["prediction"],
            lower_bound=arima_results["lower_bound"],
            upper_bound=arima_results["upper_bound"],
            volatility=garch_results["volatility"]
        )
        db.add(forecast)
        db.commit()
        
        return {
            "coin_id": coin_id,
            "auto_arima": {
                 "prediction": arima_results["prediction"],
                 "lower_bound": arima_results["lower_bound"],
                 "upper_bound": arima_results["upper_bound"],
            },
            "volatility": garch_results["volatility"],
            "experiment_id": experiment.id
        }

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
