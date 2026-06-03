import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error

def directional_accuracy(y_true, y_pred):
    """
    Calculates the directional accuracy of the predictions.
    It returns the percentage of times the model correctly predicted the direction of the price movement.
    """
    y_true_diff = np.diff(y_true)
    y_pred_diff = np.diff(y_pred)
    
    # Avoid division by zero and handle flat lines
    true_direction = np.sign(y_true_diff)
    pred_direction = np.sign(y_pred_diff)
    
    correct_directions = np.sum(true_direction == pred_direction)
    total_directions = len(true_direction)
    
    if total_directions == 0:
         return 0.0
         
    return correct_directions / total_directions

def sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculates the annualized Sharpe Ratio.
    """
    if len(returns) == 0:
        return 0.0
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0:
        return 0.0
    
    # Assuming daily returns
    return (mean_return - risk_free_rate) / std_return * np.sqrt(365)

def walk_forward_validation(model_class, df, feature_cols, target_col='close', 
                            initial_train_size=30, test_size=7, **model_kwargs):
    """
    Implements a Walk-Forward Validation Engine for Time Series models.
    
    Args:
        model_class: The ML model class to instantiate (e.g. XGBRegressor)
        df: The feature-engineered DataFrame
        feature_cols: List of column names to use as features
        target_col: The target column to predict
        initial_train_size: Minimum number of days to train on initially
        test_size: Number of days to forecast in each step
        model_kwargs: Hyperparameters for the model
        
    Returns:
        dict: A dictionary of strict evaluation metrics (RMSE, MAE, MAPE, DA)
    """
    if len(df) < initial_train_size + test_size:
        raise ValueError("Not enough data for walk forward validation.")

    predictions = []
    actuals = []
    
    # Iterate through the dataset using a sliding window
    for i in range(initial_train_size, len(df) - test_size + 1, test_size):
        # 1. Split Train and Test
        train = df.iloc[:i]
        test = df.iloc[i:i+test_size]
        
        X_train = train[feature_cols]
        y_train = train[target_col]
        
        X_test = test[feature_cols]
        y_test = test[target_col]
        
        # 2. Train Model
        model = model_class(**model_kwargs)
        model.fit(X_train, y_train)
        
        # 3. Predict
        preds = model.predict(X_test)
        
        predictions.extend(preds)
        actuals.extend(y_test.values)
        
    # Calculate Metrics
    actuals = np.array(actuals)
    predictions = np.array(predictions)
    
    rmse = np.sqrt(mean_squared_error(actuals, predictions))
    mae = mean_absolute_error(actuals, predictions)
    mape = mean_absolute_percentage_error(actuals, predictions)
    da = directional_accuracy(actuals, predictions)
    
    # Calculate Strategy Returns (Simulated simple long/short)
    # If prediction > current price, long. Else, short.
    strategy_returns = []
    # For Sharpe, we need actual prices matching predictions
    # This is a simplified Sharpe based on directional trades
    for j in range(1, len(predictions)):
         # Did we predict an increase?
         predicted_up = predictions[j] > actuals[j-1]
         actual_return = (actuals[j] - actuals[j-1]) / actuals[j-1]
         
         if predicted_up:
              strategy_returns.append(actual_return)
         else:
              strategy_returns.append(-actual_return)
              
    sharpe = sharpe_ratio(strategy_returns)

    return {
        "rmse": float(rmse),
        "mae": float(mae),
        "mape": float(mape),
        "directional_accuracy": float(da),
        "sharpe_ratio": float(sharpe)
    }
