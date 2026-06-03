import requests
from datetime import datetime, timedelta

# Basic cache to avoid rate limiting
_cache = {}

def get_crypto_data(coin_id, days=60):
    """
    Fetches historical daily market data for a given cryptocurrency from CoinGecko API.
    """
    cache_key = f"{coin_id}_{days}"
    if cache_key in _cache:
        cached_time, data = _cache[cache_key]
        # Cache for 10 minutes
        if datetime.now() - cached_time < timedelta(minutes=10):
            return data
            
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
    headers = {"User-Agent": "CryptoForecaster/2.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            _cache[cache_key] = (datetime.now(), data)
            return data
    except Exception as e:
        print(f"Error fetching data from CoinGecko: {e}")
        
    return None
