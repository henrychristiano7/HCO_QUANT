import pandas as pd
import numpy as np
import random

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi_series = 100 - (100 / (1 + rs))
    return rsi_series.fillna(50)

def compute_indicators(df: pd.DataFrame, short: int = 20, long: int = 50) -> pd.DataFrame:
    df2 = df.copy().sort_values("Date").reset_index(drop=True)
    df2['SMA_20'] = sma(df2['Close'], short)
    df2['SMA_50'] = sma(df2['Close'], long)
    df2['RSI'] = rsi(df2['Close'], period=14)
    return df2

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df2 = compute_indicators(df)
    df2['action'] = "HOLD"
    df2['AI_Confidence'] = 0
    df2['ai_comment'] = ""

    if len(df2) >= 2:
        prev = df2.iloc[-2]
        last = df2.iloc[-1]

        if (prev['SMA_20'] <= prev['SMA_50']) and (last['SMA_20'] > last['SMA_50']) and last['RSI'] < 70:
            signal = "BUY"
            confidence = random.randint(70, 90)
            comment = "🟢 Market oversold — potential buying opportunity."
        elif (prev['SMA_20'] >= prev['SMA_50']) and (last['SMA_20'] < last['SMA_50']) and last['RSI'] > 30:
            signal = "SELL"
            confidence = random.randint(70, 90)
            comment = "🔴 Market overbought — consider selling or reducing exposure."
        else:
            signal = "HOLD"
            confidence = random.randint(30, 50)
            comment = "⏸ Market neutral — monitoring recommended."

        df2.at[df2.index[-1], 'action'] = signal
        df2.at[df2.index[-1], 'AI_Confidence'] = confidence
        df2.at[df2.index[-1], 'ai_comment'] = comment
    return df2

