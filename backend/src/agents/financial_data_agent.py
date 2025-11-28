# src/agents/financial_data_agent.py

import os
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Union

# --- 1. Core Data Fetching Functions ---

def get_live_data(symbol: str) -> Dict[str, Union[str, float, int]]:
    """
    Fetches the latest minute-level live data for a stock ticker.
    
    Args:
        symbol: The stock ticker symbol (e.g., 'AAPL').
        
    Returns:
        A dictionary containing the latest price, volume, and OHLC data.
    """
    try:
        # Fetch 1 minute interval data for the last trading day (period="1d")
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="1m")

        if hist.empty:
            # Try fetching a small historical period if 1m is unavailable (e.g., pre-market)
            hist = ticker.history(period="5d", interval="1d").tail(1)
            if hist.empty:
                return {"error": f"No data returned for {symbol}."}

        last = hist.tail(1).iloc[0]

        return {
            "symbol": symbol,
            "timestamp": last.name.isoformat(), # Use index name for precise timestamp
            "price": float(last['Close']),
            "open": float(last['Open']),
            "high": float(last['High']),
            "low": float(last['Low']),
            "volume": int(last['Volume'])
        }
    except Exception as e:
        return {"error": f"Failed to fetch live data for {symbol}: {e}"}

def get_historical_data(symbol: str, period: str = "6mo", interval: str = "1d") -> Union[pd.DataFrame, Dict[str, str]]:
    """
    Fetches historical OHLCV data required for indicator calculation.
    
    Args:
        symbol: The stock ticker symbol.
        period: Timeframe to fetch (e.g., '6mo', '1y').
        interval: Granularity (e.g., '1d', '1wk').
        
    Returns:
        A pandas DataFrame with OHLCV data, or an error dictionary.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return {"error": f"No historical data found for {symbol} in the period {period}."}

        # Rename index to 'Date' and ensure necessary columns exist for strategy_agent
        df = df.reset_index().rename(columns={'Date': 'Date', 'Close': 'Close', 'Volume': 'Volume'})
        
        # Select only necessary columns to keep data clean for the pipeline
        return df[['Date', 'Close', 'Volume']]
    
    except Exception as e:
        return {"error": f"Failed to fetch historical data for {symbol}: {e}"}

# --- Example Usage (for testing the agent) ---
if __name__ == '__main__':
    # Test live data
    live_info = get_live_data("TSLA")
    print("\n--- Live Data Test ---")
    print(live_info)
    
    # Test historical data (used by strategy_agent)
    historical_df = get_historical_data("TSLA")
    if not isinstance(historical_df, dict):
        print("\n--- Historical Data Test (Last 5 Rows) ---")
        print(historical_df.tail())
