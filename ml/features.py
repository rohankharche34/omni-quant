import pandas as pd
import numpy as np
import ta

def build_features(market_info):
    """
    Constructs an advanced feature engineering pipeline using the historical market data.
    Takes the raw CoinGecko dictionary and returns a pandas DataFrame with ML-ready features.
    """
    
    # 1. Parse raw data into Pandas DataFrame
    prices = [p[1] for p in market_info['prices']]
    volumes = [v[1] for v in market_info['total_volumes']]
    timestamps = [p[0] for p in market_info['prices']]
    
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(timestamps, unit='ms'),
        'close': prices,
        'volume': volumes
    })
    
    # 2. Base Statistical Features
    df['returns'] = df['close'].pct_change()
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    
    # 3. Volatility (Rolling standard deviation of log returns)
    df['volatility_7d'] = df['log_returns'].rolling(window=7).std() * np.sqrt(365)
    df['volatility_30d'] = df['log_returns'].rolling(window=30).std() * np.sqrt(365)
    
    # 4. Momentum Indicators (ta library)
    # Relative Strength Index (RSI)
    df['rsi_14'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    
    # MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    
    # 5. Volatility Indicators
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_high'] = bollinger.bollinger_hband()
    df['bb_low'] = bollinger.bollinger_lband()
    df['bb_mavg'] = bollinger.bollinger_mavg()
    df['bb_width'] = bollinger.bollinger_wband()
    
    # 6. Trend Indicators (Moving Averages)
    df['sma_7'] = ta.trend.SMAIndicator(close=df['close'], window=7).sma_indicator()
    df['sma_30'] = ta.trend.SMAIndicator(close=df['close'], window=30).sma_indicator()
    df['ema_7'] = ta.trend.EMAIndicator(close=df['close'], window=7).ema_indicator()
    
    # 7. Volume Features
    df['volume_sma_7'] = df['volume'].rolling(window=7).mean()
    df['volume_change'] = df['volume'].pct_change()
    
    # Drop NaNs that occur due to rolling windows
    df = df.dropna().reset_index(drop=True)
    
    return df
