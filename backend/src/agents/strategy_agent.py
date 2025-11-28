# src/agents/strategy_agent.py

import pandas as pd
import numpy as np
import random
from typing import Dict, Any, Tuple

# --- Strategy Constants (Centralized Source of Truth) ---
SMA_SHORT_PERIOD = 20
SMA_LONG_PERIOD = 50
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
# Note: These constants should now be imported by src/utils/mock_data.py

# --- 1. Core Indicator Functions ---

def sma(series: pd.Series, window: int) -> pd.Series:
    """Calculates Simple Moving Average (SMA)."""
    # Using default parameters is safer for production use
    return series.rolling(window=window).mean()

def rsi(series: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    """Calculates Relative Strength Index (RSI) using standard EWMA smoothing."""
    delta = series.diff().fillna(0) 
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Use EWMA (Exponentially Weighted Moving Average) which is the industry standard for RSI
    avg_gain = gain.ewm(span=period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(span=period, adjust=False, min_periods=period).mean()

    # Calculate Relative Strength (RS)
    rs = avg_gain / avg_loss.replace(0, np.nan) 
    
    # Calculate RSI
    rsi_series = 100 - (100 / (1 + rs))
    
    # Fill initial NaNs (where min_periods hasn't been met) with 50 (neutral)
    return rsi_series.fillna(50) 

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes all required indicators and returns the enhanced DataFrame.
    Assumes df has 'Date' and 'Close' columns and is sorted chronologically.
    """
    df = df.copy() 
    
    # Use explicit, clean column names
    df['SMA_S'] = sma(df['Close'], SMA_SHORT_PERIOD)
    df['SMA_L'] = sma(df['Close'], SMA_LONG_PERIOD)
    df['RSI'] = rsi(df['Close'], RSI_PERIOD)
    
    return df

# ----------------------------------------------------------------------
# 2. Signal Logic (Decoupled from DataFrame for testability)
# ----------------------------------------------------------------------

def decide_signal(
    prev_sma_s: float, 
    prev_sma_l: float,
    last_sma_s: float,
    last_sma_l: float,
    last_rsi: float
) -> Tuple[str, int, str]:
    """
    Core business logic: determines action, confidence, and comment based on indicator values.
    Returns (signal, confidence, comment).
    """
    
    # --- BUY Conditions (Golden Cross OR strong oversold) ---
    is_golden_cross = (prev_sma_s <= prev_sma_l) and (last_sma_s > last_sma_l)
    is_oversold = last_rsi < RSI_OVERSOLD
    
    if is_golden_cross:
        signal = "BUY"
        confidence = random.randint(80, 95)
        comment = "🟢 GOLDEN CROSS detected. Short-term momentum is now above long-term."
        
    elif is_oversold:
        signal = "BUY"
        confidence = random.randint(70, 85)
        comment = f"🟢 RSI ({last_rsi:.2f}) is oversold, indicating a potential buying opportunity."
        
    # --- SELL Conditions (Death Cross OR strong overbought) ---
    else:
        is_death_cross = (prev_sma_s >= prev_sma_l) and (last_sma_s < last_sma_l)
        is_overbought = last_rsi > RSI_OVERBOUGHT
        
        if is_death_cross:
            signal = "SELL"
            confidence = random.randint(80, 95)
            comment = "🔴 DEATH CROSS detected. Short-term momentum is now below long-term."
            
        elif is_overbought:
            signal = "SELL"
            confidence = random.randint(70, 85)
            comment = f"🔴 RSI ({last_rsi:.2f}) is overbought, consider selling or reducing exposure."
            
        # --- HOLD Condition (Default/Neutral) ---
        else:
            signal = "HOLD"
            # Higher confidence if RSI is near neutral (50), indicating stability
            if (RSI_OVERSOLD < last_rsi < RSI_OVERBOUGHT):
                confidence = random.randint(50, 65)
                comment = "⏸ Market is consolidating. Awaiting clear SMA or RSI signal."
            else:
                confidence = random.randint(30, 50)
                comment = "⏸ Market neutral or mixed signals. Monitoring recommended."
                
    return signal, confidence, comment

# ----------------------------------------------------------------------
# 3. Main Agent Function (Pipeline Entry Point)
# ----------------------------------------------------------------------

def generate_latest_signal(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates the latest trading signal and commentary based on the provided data.
    """
    
    df_enhanced = compute_indicators(df)
    
    # Check for sufficient data using the longest period indicator (SMA_L)
    if len(df_enhanced) < SMA_LONG_PERIOD: 
        return {
            "action": "HOLD",
            "AI_Confidence": 10,
            "ai_comment": "Insufficient data to compute long-period indicators."
        }
    
    # Get the last two rows for the crossover logic
    # Check explicitly if we have at least 2 rows after the SMA_LONG_PERIOD length check
    if len(df_enhanced) < 2:
        return {
            "action": "HOLD",
            "AI_Confidence": 10,
            "ai_comment": "Not enough data points for crossover logic."
        }
    
    prev = df_enhanced.iloc[-2]
    last = df_enhanced.iloc[-1]
    
    # Extract necessary indicator values
    prev_sma_s = prev['SMA_S']
    prev_sma_l = prev['SMA_L']
    last_sma_s = last['SMA_S']
    last_sma_l = last['SMA_L']
    last_rsi = last['RSI']

    # Call the decoupled logic function
    signal, confidence, comment = decide_signal(
        prev_sma_s, prev_sma_l, 
        last_sma_s, last_sma_l, 
        last_rsi
    )
    
    # Return a structured dictionary for the API/Pipeline
    return {
        "action": signal,
        "AI_Confidence": confidence,
        "ai_comment": comment,
        "latest_close": last['Close'],
        "latest_date": str(last['Date']), 
    }
