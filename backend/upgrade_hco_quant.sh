#!/bin/bash

echo "🚀 Starting HCO-Quant Hackathon Upgrade..."

PROJECT_ROOT="$HOME/HCO-Quant"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
JAC_DIR="$BACKEND_DIR/jaseci_ai"

echo "📁 Creating folder structure..."
mkdir -p $BACKEND_DIR
mkdir -p $FRONTEND_DIR
mkdir -p $JAC_DIR/workflows
mkdir -p $JAC_DIR/models

###############################################
# 1) Create requirements.txt
###############################################

cat > $BACKEND_DIR/requirements.txt << 'EOF'
fastapi
uvicorn
httpx
python-dotenv
jaseci
jaseci-ai-kit
yfinance
EOF

echo "📄 Created requirements.txt"

###############################################
# 2) Create environment file
###############################################

cat > $BACKEND_DIR/.env << 'EOF'
OPENAI_API_KEY=your_openai_key_here
VIRUSTOTAL_API_KEY=your_virustotal_key_here
EOF

echo "🔐 Created .env file"

###############################################
# 3) Create Jaseci Jac workflow
###############################################

cat > $JAC_DIR/workflows/hco_quant_ai.jac << 'EOF'
walker explain_signal {
    can ai.explain_market(flavor="openai", prompt=message) -> resp;
    return resp;
}

walker detect_threat {
    can ai.check_url(flavor="virustotal", url=threat_url) -> result;
    return result;
}
EOF

echo "🤖 Created Jac AI workflows"

###############################################
# 4) Create data_agent.py (with Yahoo Finance)
###############################################

cat > $BACKEND_DIR/data_agent.py << 'EOF'
import yfinance as yf

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
EOF

echo "📡 Created data_agent.py"

###############################################
# 5) Create hco_quant_api.py (FastAPI backend)
###############################################

cat > $BACKEND_DIR/hco_quant_api.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio

from data_agent import get_live_data
from jaseci_serv.jac import JsOrc

app = FastAPI(title="HCO Quant AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orc = JsOrc()
orc.register_std()
orc.register_ai()

jac_code_path = os.path.join(os.path.dirname(__file__), "jaseci_ai/workflows/hco_quant_ai.jac")
orc.load_jac(jac_code_path)

@app.get("/price/{symbol}")
async def price(symbol: str):
    return get_live_data(symbol)

@app.get("/explain")
async def explain(prompt: str):
    resp = orc.call("explain_signal", message=prompt)
    return resp

@app.get("/threat")
async def threat(url: str):
    resp = orc.call("detect_threat", threat_url=url)
    return resp

@app.get("/")
def index():
    return {"status": "HCO Quant AI Backend Running"}
EOF

echo "🧠 Created hco_quant_api.py"

###############################################
# 6) Install dependencies
###############################################

echo "📦 Installing Python dependencies..."
pip install -r $BACKEND_DIR/requirements.txt

###############################################
# 7) Done!
###############################################

echo ""
echo "✅ HCO-Quant Hackathon Upgrade Complete!"
echo "Run backend now:"
echo "---------------------------------------"
echo "cd $BACKEND_DIR"
echo "uvicorn hco_quant_api:app --reload --host 0.0.0.0 --port 8000"
echo "---------------------------------------"
echo ""
echo "Frontend stays unchanged — connect to API via:"
echo "http://localhost:8000"
echo ""
echo "🚀 You're ready for the Hackathon!"

