import pmdarima as pm
from arch import arch_model
import warnings

def predict_with_auto_arima(prices, interval):
    """
    Trains an Auto-ARIMA model on the fly, dynamically finding the best p,d,q.
    Returns the prediction and the 95% confidence intervals.
    """
    if not prices or len(prices) < 30:
        raise ValueError("Not enough historical data to train Auto-ARIMA model.")
        
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        # Auto-ARIMA searches for the best parameters
        model = pm.auto_arima(
            prices, 
            start_p=1, start_q=1,
            max_p=2, max_q=2, m=1, # No seasonality for speed
            start_P=0, seasonal=False,
            d=1, D=None, trace=False,
            error_action='ignore',  
            suppress_warnings=True, 
            stepwise=True
        )
        
        # Forecast future values and get 95% confidence intervals
        forecast, conf_int = model.predict(n_periods=interval, return_conf_int=True)
        
        final_prediction = list(forecast)[-1]
        lower_bound = conf_int[-1][0]
        upper_bound = conf_int[-1][1]
        
        return {
            "prediction": float(final_prediction),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound)
        }

def predict_volatility(prices, interval):
    """
    Models the volatility (risk) using GARCH(1,1).
    """
    if len(prices) < 30:
        return 0.0
        
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        # Calculate returns (percentage change)
        returns = [100 * (prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Fit GARCH(1,1)
        am = arch_model(returns, vol='Garch', p=1, q=1, rescale=False)
        res = am.fit(disp='off')
        
        # Forecast variance
        forecasts = res.forecast(horizon=interval)
        variance = forecasts.variance.values[-1, -1]
        
        # Return expected standard deviation (volatility)
        return float(variance ** 0.5)
