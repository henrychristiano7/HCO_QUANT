import asyncio
import random
import datetime
import pandas as pd
import numpy as np
import os

# ---------------------------
# SMA and RSI helpers
# ---------------------------
def sma(series: pd.Series, window: int = 20) -> pd.Series:
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

# ---------------------------
# Generate mock OHLCV
# ---------------------------
def generate_mock_ohlcv(symbol: str, days: int = 50) -> pd.DataFrame:
    base_price = {
        "AAPL": 310,
        "TSLA": 430,
        "MSFT": 280,
        "GOOGL": 135,
        "AMZN": 140,
    }.get(symbol.upper(), random.uniform(100, 500))

    dates = [datetime.datetime.today() - datetime.timedelta(days=i) for i in reversed(range(days))]
    close_prices = base_price * np.cumprod(np.random.uniform(0.985, 1.015, days))
    close_prices = np.round(close_prices, 2)
    open_prices = np.round(close_prices * np.random.uniform(0.985, 1.015, days), 2)
    high_prices = np.round(np.maximum(open_prices, close_prices) * np.random.uniform(1.0, 1.01, days), 2)
    low_prices = np.round(np.minimum(open_prices, close_prices) * np.random.uniform(0.99, 1.0, days), 2)
    volume = np.random.randint(100_000, 1_000_000, days)

    df = pd.DataFrame({
        "Date": dates,
        "Open": open_prices,
        "High": high_prices,
        "Low": low_prices,
        "Close": close_prices,
        "Volume": volume
    })
    df = df.sort_values("Date").reset_index(drop=True)
    return df

# ---------------------------
# Compute signals with AI confidence & comment
# ---------------------------
def compute_signals(df: pd.DataFrame, symbol: str) -> dict:
    df['SMA_20'] = sma(df['Close'], 20)
    df['SMA_50'] = sma(df['Close'], 50)
    df['RSI'] = rsi(df['Close'], 14)

    last_idx = len(df) - 1
    prev = df.iloc[last_idx - 1]
    last = df.iloc[last_idx]

    rand_factor = random.uniform(-5, 5)
    rsi_adj = last['RSI'] + rand_factor

    if (prev['SMA_20'] <= prev['SMA_50'] and last['SMA_20'] > last['SMA_50']) or rsi_adj < 40:
        signal = "BUY"
        confidence = random.randint(70, 90)
        color = "green"
        ai_comment = "🟢 Market oversold — potential buying opportunity."
    elif (prev['SMA_20'] >= prev['SMA_50'] and last['SMA_20'] < last['SMA_50']) or rsi_adj > 60:
        signal = "SELL"
        confidence = random.randint(70, 90)
        color = "red"
        ai_comment = "🔴 Market overbought — consider selling or reducing exposure."
    else:
        signal = "HOLD"
        confidence = random.randint(30, 50)
        color = "gray"
        ai_comment = "⏸ Market neutral — monitoring recommended."

    return {
        "Symbol": symbol.upper(),
        "Close": round(last['Close'], 2),
        "SMA_20": round(last['SMA_20'], 2),
        "RSI": round(last['RSI'], 2),
        "Signal": signal,
        "AI_Confidence": f"{confidence}%",
        "confidence": confidence,
        "Color": color,
        "ai_comment": ai_comment,
        "Last_Updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ---------------------------
# Async single symbol
# ---------------------------
async def generate_mock_data(symbol: str):
    await asyncio.sleep(random.uniform(0.05,0.25))
    df = generate_mock_ohlcv(symbol, days=50)
    data = compute_signals(df, symbol)

    # ---------------------------
    # Save history CSV per symbol
    # ---------------------------
    history_dir = os.path.expanduser("~/HCO-Quant/data/history")
    os.makedirs(history_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(history_dir, f"{symbol.upper()}_{timestamp}.csv")
    pd.DataFrame([data]).to_csv(filename, index=False)

    return data

# ---------------------------
# Async multi-symbol HTML
# ---------------------------
async def generate_mock_html(symbols: str):
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    tasks = [generate_mock_data(sym) for sym in symbol_list]
    results = await asyncio.gather(*tasks)

    html = f"""
    <html>
    <head>
        <title>📊 Multi-Symbol SMA + RSI Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f4f7fb; color:#333; text-align:center; padding:30px; }}
            h1 {{ color:#0074D9; margin-bottom:20px; }}
            table {{ border-collapse: separate; border-spacing: 0; margin:20px auto; width:95%; box-shadow:0 5px 15px rgba(0,0,0,0.1); border-radius:12px; overflow:hidden; }}
            th, td {{ padding:12px 15px; border:1px solid #ddd; text-align:center; }}
            th {{ background-color:#0074D9; color:white; text-shadow:0 0 4px rgba(0,255,255,0.4); }}
            tr:nth-child(even) {{ background-color:#f9f9f9; }}
            .green {{ color:#00c853; font-weight:bold; text-shadow:0 0 6px rgba(0,200,83,0.5); }}
            .red {{ color:#d50000; font-weight:bold; text-shadow:0 0 6px rgba(213,0,0,0.5); }}
            .gray {{ color:#888; font-weight:bold; }}
            .ai-comment {{ font-style:italic; font-size:0.9rem; margin-top:5px; }}
            .timestamp {{ margin-top:10px; font-size:14px; color:#555; }}
            tr:hover {{ background-color: rgba(0, 120, 255, 0.05); }}
        </style>
    </head>
    <body>
        <h1>📊 Multi-Symbol SMA + RSI Dashboard (AI-powered)</h1>
        <table>
            <tr>
                <th>Symbol</th>
                <th>Close ($)</th>
                <th>SMA 20</th>
                <th>RSI</th>
                <th>Signal</th>
                <th>AI Confidence</th>
                <th>AI Comment</th>
                <th>Last Updated</th>
            </tr>
    """

    for d in results:
        html += f"""
            <tr>
                <td>{d['Symbol']}</td>
                <td>{d['Close']}</td>
                <td>{d['SMA_20']}</td>
                <td>{d['RSI']}</td>
                <td class="{d['Color']}">{d['Signal']}</td>
                <td>{d['AI_Confidence']}</td>
                <td class="ai-comment">{d['ai_comment']}</td>
                <td>{d['Last_Updated']}</td>
            </tr>
        """

    html += "</table></body></html>"
    return html

