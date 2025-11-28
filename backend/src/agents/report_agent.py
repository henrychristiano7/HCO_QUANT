# src/agents/report_agent.py (FINAL COMPLETE VERSION)

import matplotlib
matplotlib.use("Agg")  # headless rendering for server
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# -----------------------------
# History storage configuration
# -----------------------------
# Corrected path to be inside the HCO-Quant project folder.
HISTORY_DIR = os.path.join(
    os.path.expanduser("~"), 
    "HCO-Quant", 
    "data", 
    "history"
)

# Ensure the directory exists.
os.makedirs(HISTORY_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(HISTORY_DIR, "trade_history.json")

# -----------------------------
# Helper Functions
# -----------------------------
def _encode_fig_to_base64(fig: plt.Figure) -> str:
    """Encode a Matplotlib figure to a base64 PNG string."""
    buf = io.BytesIO()
    fig.tight_layout() 
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

# -----------------------------
# Data Processing Function
# -----------------------------
def process_latest_signal(symbol: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms the strategy_agent's output into a standardized history entry.
    
    CRITICAL CHANGE: Added 'llm_commentary' field.
    """
    return {
        "timestamp": datetime.now().isoformat(), 
        "symbol": symbol,
        "date": signal_data.get('latest_date', datetime.now().strftime("%Y-%m-%d")),
        "action": signal_data.get('action', 'HOLD'),
        "price": signal_data.get('latest_close'),
        "confidence": signal_data.get('AI_Confidence', 0),
        "rationale": signal_data.get('ai_comment', ''),
        # NEW: Include the detailed LLM commentary if it exists (it's optional in the pipeline)
        "llm_commentary": signal_data.get('llm_commentary', None), 
        "data_source": signal_data.get('data_source', 'UNKNOWN'), 
    }

# -----------------------------
# History Functions (Robust Load/Save)
# -----------------------------
def load_history() -> List[Dict[str, Any]]:
    """
    Load all historical trade/decision records. 
    Handles missing or corrupted file gracefully by returning an empty list.
    """
    try:
        if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
    except json.JSONDecodeError:
        print(f"[WARN] History file '{HISTORY_FILE}' corrupted, starting new history.")
    except Exception as e:
        print(f"[WARN] Error loading history: {e}")
        
    return []

def save_history_entry(entry: Dict):
    """
    Append a decision record to trade_history.json.
    Uses atomic write to avoid corruption and ensures JSON serialization is safe.
    """
    try:
        data = load_history() 
        data.append(entry)
        data.sort(key=lambda x: x.get('timestamp', '0'), reverse=False) 
        
        tmp_file = HISTORY_FILE + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(data, f, indent=2, default=str) 
            
        os.replace(tmp_file, HISTORY_FILE)
        
    except Exception as e:
        print(f"[ERROR] Could not save history entry to {HISTORY_FILE}: {e}")

# -----------------------------
# Charting Function 
# -----------------------------
def create_chart(df: pd.DataFrame, symbol: str, decisions: Optional[List[Dict]] = None) -> str:
    """
    Create a chart with Close, SMA_S, SMA_L and volume subplot.
    Marks BUY/SELL points if provided in decisions.
    Returns base64-encoded PNG string.
    """
    df['Date'] = pd.to_datetime(df['Date'])
    decisions = decisions or []
    
    buys = [d for d in decisions if d.get('action') == "BUY"]
    sells = [d for d in decisions if d.get('action') == "SELL"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), 
                                    gridspec_kw={'height_ratios':[3,1]}, 
                                    sharex=True)

    # Main Price/Indicator Plot
    ax1.plot(df['Date'], df['Close'], label='Close', linewidth=1.5, color='blue')
    ax1.plot(df['Date'], df.get('SMA_S', df['Close']), label='SMA_S', linestyle='--', color='orange')
    ax1.plot(df['Date'], df.get('SMA_L', df['Close']), label='SMA_L', linestyle='--', color='purple')

    # Decision Markers
    if buys:
        buy_dates = [pd.to_datetime(b['date']) for b in buys]
        buy_prices = [b['price'] for b in buys]
        ax1.scatter(buy_dates, buy_prices, marker='^', color='green', s=100, label='Buy Signal', zorder=5)
    if sells:
        sell_dates = [pd.to_datetime(s['date']) for s in sells]
        sell_prices = [s['price'] for s in sells]
        ax1.scatter(sell_dates, sell_prices, marker='v', color='red', s=100, label='Sell Signal', zorder=5)

    ax1.set_title(f"Quant Strategy Analysis for {symbol}")
    ax1.legend(loc='upper left')
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Volume Subplot
    ax2.bar(df['Date'], df['Volume'], color='gray', alpha=0.6, width=0.8)
    ax2.set_ylabel("Volume")
    ax2.set_xlabel("Date")
    ax2.grid(axis='y', linestyle=':', alpha=0.6)
    
    # Format x-axis dates cleanly
    ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=35, ha='right')

    return _encode_fig_to_base64(fig)
