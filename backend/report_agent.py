# report_agent.py
import matplotlib
matplotlib.use("Agg")  # headless rendering for server
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

# -----------------------------
# History storage configuration
# -----------------------------
HISTORY_DIR = os.path.expanduser("~/HCO-Quant-data-history")
os.makedirs(HISTORY_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(HISTORY_DIR, "trade_history.json")

# -----------------------------
# Helper Functions
# -----------------------------
def _encode_fig_to_base64(fig: plt.Figure) -> str:
    """Encode a Matplotlib figure to a base64 PNG string."""
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

# -----------------------------
# Charting Function
# -----------------------------
def create_chart(df: pd.DataFrame, symbol: str, decisions: Optional[List[Dict]] = None) -> str:
    """
    Create a chart with Close, SMA20, SMA50 and volume subplot.
    Marks BUY/SELL points if provided in decisions.
    Returns base64-encoded PNG string.
    """
    decisions = decisions or []
    buys = [d for d in decisions if d.get('action') == "BUY"]
    sells = [d for d in decisions if d.get('action') == "SELL"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), gridspec_kw={'height_ratios':[3,1]}, sharex=True)

    ax1.plot(df['Date'].astype(str), df['Close'], label='Close', linewidth=1.5)
    ax1.plot(df['Date'].astype(str), df.get('sma20', df['Close']), label='SMA20', linestyle='--')
    ax1.plot(df['Date'].astype(str), df.get('sma50', df['Close']), label='SMA50', linestyle='--')

    if buys:
        ax1.scatter([b['date'] for b in buys], [b['price'] for b in buys], marker='^', color='green', s=70, label='Buy')
    if sells:
        ax1.scatter([s['date'] for s in sells], [s['price'] for s in sells], marker='v', color='red', s=70, label='Sell')

    ax1.set_title(f"{symbol} Price + SMA Strategy")
    ax1.legend(loc='upper left')
    ax1.grid(True)

    ax2.bar(df['Date'].astype(str), df['Volume'], color='gray', alpha=0.6)
    ax2.set_ylabel("Volume")
    for lbl in ax1.get_xticklabels():
        lbl.set_rotation(35)
        lbl.set_ha('right')

    return _encode_fig_to_base64(fig)

# -----------------------------
# History Functions
# -----------------------------
def save_history_entry(entry: Dict):
    """
    Append a decision record to trade_history.json.
    Uses atomic write to avoid corruption.
    """
    try:
        data = load_history()
        data.append(entry)
        tmp_file = HISTORY_FILE + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_file, HISTORY_FILE)
    except Exception as e:
        print(f"[WARN] Could not save history entry: {e}")

def load_history() -> List[Dict]:
    """Load all historical trade/decision records."""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []

# -----------------------------
# Generative Summary Function
# -----------------------------
def generate_summary(decisions: List[Dict]) -> str:
    """
    Generate a textual summary of the latest AI decisions.
    """
    summary = "📊 HCO Quant AI Report:\n"
    for d in decisions:
        summary += f"- {d.get('symbol', 'N/A')} ({d.get('date', 'N/A')}): {d.get('action', 'HOLD')} | {d.get('rationale', '')} (Confidence: {d.get('confidence', 0)}%)\n"
    return summary
