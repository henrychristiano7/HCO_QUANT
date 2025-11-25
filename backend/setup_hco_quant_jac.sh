#!/bin/bash
set -euo pipefail

BACKEND_DIR="$HOME/HCO-Quant/backend"
JAC_DIR="$BACKEND_DIR/jac"
PY_WRAPPER="$BACKEND_DIR/hco_quant_jac.py"

# ----------------------------
# 1️⃣ Create Jac folder
# ----------------------------
mkdir -p "$JAC_DIR"
echo "📁 Jac folder created at $JAC_DIR"

# ----------------------------
# 2️⃣ Create models.jac
# ----------------------------
cat > "$JAC_DIR/models.jac" <<'EOF'
# ----------------------------
# Jac Models
# ----------------------------

node User:
    username: str
    mastery_score: int = 0

node Lesson:
    title: str
    content: str
    difficulty: int = 1

node Quiz:
    question: str
    answer: str
    lesson_id: str
EOF
echo "📝 Created models.jac"

# ----------------------------
# 3️⃣ Create walkers.jac
# ----------------------------
cat > "$JAC_DIR/walkers.jac" <<'EOF'
# ----------------------------
# Jac Walkers
# ----------------------------

walker populate_demo():
    # Sample Users
    spawn here User(username="alice")
    spawn here User(username="bob")
    spawn here User(username="charlie")
    
    # Sample Lessons
    spawn here Lesson(title="Intro to SMA", content="Simple Moving Average basics", difficulty=1)
    spawn here Lesson(title="RSI Interpretation", content="How RSI indicates overbought/oversold", difficulty=2)
    spawn here Lesson(title="Advanced Trading Strategies", content="Combining SMA & RSI for entries", difficulty=3)
    
    yield "✅ Demo users and lessons populated successfully."

walker serve_content():
    # Returns lessons to user
    lessons = [l for l in here if l.__class__ == Lesson]
    yield lessons
EOF
echo "📝 Created walkers.jac"

# ----------------------------
# 4️⃣ Create Python wrapper
# ----------------------------
cat > "$PY_WRAPPER" <<'EOF'
import os
import yfinance as yf
from jaseci.jsorc.jsorc import JsOrc

# ----------------------------
# Load Jac
# ----------------------------
orc = JsOrc()
orc.load_jac(os.path.join(os.path.dirname(__file__), "jac/models.jac"))
orc.load_jac(os.path.join(os.path.dirname(__file__), "jac/walkers.jac"))

# ----------------------------
# LLM placeholder (demo)
# ----------------------------
def call_llm(prompt: str):
    # Replace with your LLM call, e.g., OpenAI
    return f"LLM response to: {prompt}"

# ----------------------------
# Real OHLCV using yfinance
# ----------------------------
def generate_real_ohlcv(symbol: str, days: int = 50):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=f"{days}d")
    if df.empty:
        raise ValueError(f"No data for {symbol}")
    df = df.reset_index().rename(columns={"Date":"Date","Open":"Open","High":"High","Low":"Low","Close":"Close","Volume":"Volume"})
    return df

# ----------------------------
# Call walkers
# ----------------------------
def populate_demo():
    return orc.call("populate_demo")

def serve_content():
    return orc.call("serve_content")

def analyze_with_llm(symbol: str):
    df = generate_real_ohlcv(symbol)
    last_close = df['Close'].iloc[-1]
    signal = call_llm(f"Analyze {symbol}, last close {last_close}")
    return {"symbol": symbol, "signal": signal, "last_close": last_close}
EOF
echo "📝 Created hco_quant_jac.py wrapper"

# ----------------------------
# 5️⃣ Instructions
# ----------------------------
echo -e "\n✅ Setup complete!"
echo "Next steps:"
echo "1. In Python, activate venv and test wrapper:"
echo "   from hco_quant_jac import populate_demo, serve_content, analyze_with_llm"
echo "   populate_demo()  # populates demo users and lessons"
echo "   serve_content()  # returns lessons"
echo "   analyze_with_llm('AAPL')  # example analysis"
echo "2. Add FastAPI endpoints in hco_quant_api.py to call these functions if needed."
