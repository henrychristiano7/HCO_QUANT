#!/bin/bash

BASE_DIR="/home/henry/HCO-Quant/backend"
JAC_DIR="$BASE_DIR/jac"

echo "[INFO] Cleaning old Jac folder..."
rm -rf "$JAC_DIR"

echo "[INFO] Creating required folders..."
mkdir -p "$JAC_DIR"/{walkers,models,workspace}

echo "[INFO] Creating walker templates..."

# fetch_data.jac
cat > "$JAC_DIR/walkers/fetch_data.jac" <<EOL
walker fetch_data(symbol) {
    can run;
    report {
        "symbol": symbol,
        "message": "Data fetch executed"
    };
}
EOL

# analyze_stock.jac
cat > "$JAC_DIR/walkers/analyze_stock.jac" <<EOL
walker analyze_stock(symbol, data) {
    can run;

    llm_out = by.explain("Explain the trend for " + symbol);

    report {
        "symbol": symbol,
        "analysis": llm_out
    };
}
EOL

# threat_scan.jac
cat > "$JAC_DIR/walkers/threat_scan.jac" <<EOL
walker threat_scan(url) {
    can run;

    risk = by.explain("Classify risk: " + url);

    report {
        "url": url,
        "risk": risk
    };
}
EOL

echo "[INFO] Creating model templates..."

# ticker.jac
cat > "$JAC_DIR/models/ticker.jac" <<EOL
node Ticker {
    has symbol: str;
    has name: str;
}
EOL

# market_scenario.jac
cat > "$JAC_DIR/models/market_scenario.jac" <<EOL
node MarketScenario {
    has symbol: str;
    has trend: str;
    has risk: str;
}
EOL

echo "[INFO] Creating AI integration file..."

# hco_quant_llm.py
cat > "$JAC_DIR/hco_quant_llm.py" <<'EOL'
import os
from byllm.llm import Model
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = os.getenv("BYLLM_MODEL", "gemini/gemini-2.0-flash")

llm = Model(model=LLM_MODEL)

async def explain_market(prompt: str):
    return await llm.run(prompt)

async def threat_detect(text: str):
    q = f"Classify this URL or text for phishing/scam/malware risk:\n{text}"
    return await llm.run(q)
EOL

echo "[INFO] Creating Jaseci bridge file..."

# jac_bridge.py
cat > "$JAC_DIR/jac_bridge.py" <<'EOL'
from jaseci.jac.jac import Jac
from jaseci.jsorc.live_actions import load_actions

class JacBridge:
    def __init__(self):
        self.jac = Jac()
        load_actions(self.jac)

    def run_walker(self, path: str, walker: str, params=None):
        mod = self.jac.load_module(path)
        return self.jac.run_walker(mod, walker, params or {})
EOL

echo "[INFO] Creating FastAPI API template..."

# api.py
cat > "$BASE_DIR/api.py" <<'EOL'
from fastapi import FastAPI
from jac.jac_bridge import JacBridge
from jac.hco_quant_llm import explain_market, threat_detect

bridge = JacBridge()
app = FastAPI()

@app.get("/price/{symbol}")
def get_price(symbol: str):
    return bridge.run_walker("jac/walkers/fetch_data.jac", "fetch_data", {"symbol": symbol})

@app.get("/analyze/{symbol}")
async def analyze(symbol: str):
    return await explain_market(f"Analyze stock {symbol}")

@app.get("/threat")
async def threat(url: str):
    return await threat_detect(url)
EOL

echo "[INFO] Creating run script..."
# run.sh
cat > "$BASE_DIR/run.sh" <<'EOL'
#!/bin/bash
source venv/bin/activate
echo "[INFO] Starting HCO_QUANT API..."
uvicorn api:app --reload --host 0.0.0.0 --port 8000
EOL

chmod +x "$BASE_DIR/run.sh"

echo "[SUCCESS] HCO-Quant Jac Cloud structure created!"
echo "Run server with: $BASE_DIR/run.sh"
