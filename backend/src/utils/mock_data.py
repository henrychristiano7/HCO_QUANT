# src/utils/mock_data.py (CORRECTED CODE)

import pandas as pd
import numpy as np
import random
import datetime
from typing import Dict, Union

# --- Constants for Strategy Agent Rules ---
# Define these here for internal consistency when forcing signals
SMA_SHORT_PERIOD = 20
SMA_LONG_PERIOD = 50
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

def _calculate_sma(series: pd.Series, window: int) -> pd.Series:
    """Helper to calculate SMA within the mock generator."""
    return series.rolling(window=window).mean()

def _force_signal_on_last_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Randomly manipulates the last 'Close' price to GUARANTEE a specific signal 
    for diverse testing, using increased price shocks.
    """
    if len(df) < SMA_LONG_PERIOD:
        # Cannot force signal if there aren't enough rows to calculate SMAs
        return df

    # 1. Calculate SMAs on the generated data (required for comparison)
    df['SMA_20'] = _calculate_sma(df['Close'], SMA_SHORT_PERIOD)
    df['SMA_50'] = _calculate_sma(df['Close'], SMA_LONG_PERIOD)
    
    # 2. Decide what kind of signal to force (increased probability for active signals)
    force_type = random.choices(
        ['BUY_CROSS', 'SELL_CROSS', 'RSI_OVERSOLD', 'RSI_OVERBOUGHT', 'NATURAL_HOLD'],
        weights=[0.20, 0.20, 0.15, 0.15, 0.30],  # 70% chance of forcing a signal
        k=1
    )[0]
    
    last_idx = df.index[-1]
    prev_idx = df.index[-2]

    # Get necessary values before manipulation
    prev_close = df.at[prev_idx, 'Close']
    last_close = df.at[last_idx, 'Close']

    # --- Force Actions (using increased volatility) ---
    
    if force_type == 'NATURAL_HOLD':
        # Don't force anything; let the random walk determine the signal.
        pass
        
    elif force_type == 'BUY_CROSS':
        # Force BUY Cross: Set a sharp 10% jump to drag the SMA 20 above SMA 50.
        df.at[last_idx, 'Close'] = last_close * 1.10
        
    elif force_type == 'SELL_CROSS':
        # Force SELL Cross: Set a sharp 10% drop to drag the SMA 20 below SMA 50.
        df.at[last_idx, 'Close'] = last_close * 0.90

    elif force_type == 'RSI_OVERSOLD':
        # Force OVERSOLD: Set a severe 15% drop over the last price.
        df.at[last_idx, 'Close'] = prev_close * 0.85 
            
    elif force_type == 'RSI_OVERBOUGHT':
        # Force OVERBOUGHT: Set a severe 15% jump over the last price.
        df.at[last_idx, 'Close'] = prev_close * 1.15

    # 3. Drop temp SMAs before returning (as strategy_agent will recalculate)
    return df.drop(columns=['SMA_20', 'SMA_50'])


def generate_mock_ohlcv(
    symbol: str, 
    days: int = 60, 
    interval_hours: Union[float, int] = 6, 
    volatility: float = 0.005
) -> pd.DataFrame:
    """
    Generates a DataFrame of randomized OHLCV data at a high frequency (hourly)
    and then conditionally forces a clear signal for dynamic testing.
    """
    
    # 1. Determine Base Price and N
    base_price = {
        "AAPL": 310, "TSLA": 430, "MSFT": 280, 
        "GOOGL": 135, "AMZN": 140,
    }.get(symbol.upper(), random.uniform(100, 500))

    N = days * int(interval_hours) 
    
    # 2. Generate Timestamps and Prices (Random Walk)
    dates = [
        datetime.datetime.now() - datetime.timedelta(hours=i) 
        for i in reversed(range(N))
    ]
    
    price_change_factor = np.random.uniform(1.0 - volatility, 1.0 + volatility, N)
    close_prices = base_price * np.cumprod(price_change_factor)
    close_prices = np.round(close_prices, 2)
    
    # 3. Generate OHLCV Data
    open_prices = np.round(close_prices * np.random.uniform(0.998, 1.002, N), 2)
    high_prices = np.round(np.maximum(open_prices, close_prices) * np.random.uniform(1.0, 1.001, N), 2)
    low_prices = np.round(np.minimum(open_prices, close_prices) * np.random.uniform(0.999, 1.0, N), 2)
    volume = np.random.randint(50_000, 500_000, N)

    df = pd.DataFrame({
        "Date": dates,
        "Open": open_prices,
        "High": high_prices,
        "Low": low_prices,
        "Close": close_prices,
        "Volume": volume
    })
    
    df = df.sort_values("Date").reset_index(drop=True)
    
    # 4. FORCE A SIGNAL (Key step for testing)
    df = _force_signal_on_last_rows(df)

    # 5. Return the required columns
    return df[['Date', 'Close', 'Volume']]


if __name__ == '__main__':
    # Test generation to ensure signals are forced
    print("--- Mock Data Test with Increased Forced Signals ---")
    
    # Run loop to demonstrate different signals
    for _ in range(10):
        mock_df = generate_mock_ohlcv("TEST", days=60, interval_hours=6)
        
        # Recalculate indicators for verification
        mock_df['SMA_20'] = _calculate_sma(mock_df['Close'], SMA_SHORT_PERIOD)
        mock_df['SMA_50'] = _calculate_sma(mock_df['Close'], SMA_LONG_PERIOD)
        
        # Simple signal check (for display purposes only)
        last = mock_df.iloc[-1]
        prev = mock_df.iloc[-2]
        
        signal = "HOLD"
        if (prev['SMA_20'] <= prev['SMA_50']) and (last['SMA_20'] > last['SMA_50']):
             signal = "BUY (Cross)"
        elif (prev['SMA_20'] >= prev['SMA_50']) and (last['SMA_20'] < last['SMA_50']):
             signal = "SELL (Cross)"

        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Signal Check: {signal} | Close: {last['Close']:.2f} | SMA20: {last['SMA_20']:.2f} | SMA50: {last['SMA_50']:.2f}")
