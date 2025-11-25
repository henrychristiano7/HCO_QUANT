# data_agent.py
import os
import requests
import yfinance as yf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
VT_API_KEY = os.getenv("VT_API_KEY")
if not VT_API_KEY:
    raise ValueError("VirusTotal API key not found in .env")

# ----------------------------
# 1️⃣ Live stock data using yfinance
# ----------------------------
def get_live_data(symbol: str):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d", interval="1m")

    if hist.empty:
        return {"error": "No data returned"}

    last = hist.tail(1).iloc[0]

    return {
        "symbol": symbol,
        "price": float(last['Close']),
        "open": float(last['Open']),
        "high": float(last['High']),
        "low": float(last['Low']),
        "volume": int(last['Volume'])
    }

# ----------------------------
# 2️⃣ VirusTotal file or URL check
# ----------------------------
def vt_file_report(file_hash: str):
    """
    Query VirusTotal for a file hash report.
    """
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {"x-apikey": VT_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": f"VirusTotal API error: {response.status_code}"}

    return response.json()


def vt_url_report(url_to_check: str):
    """
    Query VirusTotal for a URL report.
    """
    url = "https://www.virustotal.com/api/v3/urls"
    headers = {"x-apikey": VT_API_KEY}
    
    # VirusTotal requires URL to be base64 encoded without trailing '='
    import base64
    url_id = base64.urlsafe_b64encode(url_to_check.encode()).decode().strip("=")
    
    vt_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    response = requests.get(vt_url, headers=headers)
    
    if response.status_code != 200:
        return {"error": f"VirusTotal API error: {response.status_code}"}
    
    return response.json()

