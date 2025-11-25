# data_agent.py
# Handles data retrieval, cleaning, and caching for HCO Quant
import yfinance as yf
import pandas as pd

def fetch_data(symbol="AAPL", period="1y", interval="1d"):
    print(f"📊 Fetching market data for {symbol}...")
    data = yf.download(symbol, period=period, interval=interval)
    return data

if __name__ == "__main__":
    df = fetch_data()
    print(df.head())
