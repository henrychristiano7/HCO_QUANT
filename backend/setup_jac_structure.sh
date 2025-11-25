#!/usr/bin/env bash

set -e

JAC_ROOT="/home/henry/HCO-Quant/backend/jac"

echo "[INFO] Cleaning existing jac folder..."
rm -rf "$JAC_ROOT"
mkdir -p "$JAC_ROOT"

echo "[INFO] Creating project structure..."
mkdir -p "$JAC_ROOT/walkers"
mkdir -p "$JAC_ROOT/models"
mkdir -p "$JAC_ROOT/workspace"

#############################################
# MODELS
#############################################
echo "[INFO] Creating model templates..."

cat << 'EOF' > "$JAC_ROOT/models/ticker.jac"
# Model: Ticker data structure
struct Ticker {
    name: str;
    price: float;
    currency: str;
}
EOF

cat << 'EOF' > "$JAC_ROOT/models/market_scenario.jac"
# AI-driven Market Scenario Definition
struct MarketScenario {
    ticker: str;
    direction: str;     # "up", "down", "sideways"
    confidence: float;  # 0–1
    reasoning: str;
}
EOF


#############################################
# WALKERS
#############################################
echo "[INFO] Creating walker templates..."

# Walker: analyze_stock
cat << 'EOF' > "$JAC_ROOT/walkers/analyze_stock.jac"
import { MarketScenario } from "../models/market_scenario.jac";

walker analyze_stock(ticker: str, days: int = 30) -> MarketScenario by llm {

    """AI analyzes the stock and returns a structured market scenario."""

    return MarketScenario(
        ticker = ticker,
        direction = "unknown",
        confidence = 0.0,
        reasoning = "LLM has not provided output yet."
    );
}
EOF

# Walker: fetch_data
cat << 'EOF' > "$JAC_ROOT/walkers/fetch_data.jac"
walker fetch_data(ticker: str) -> dict by llm {

    """LLM produces a JSON blob describing the stock profile."""

    return {
        "ticker": ticker,
        "sector": "unknown",
        "volatility": "medium",
        "notes": "LLM should refine this output."
    };
}
EOF

# Walker: alert_signals
cat << 'EOF' > "$JAC_ROOT/walkers/alert_signals.jac"
walker alert_signals(ticker: str) -> list by llm {

    """LLM generates a list of trading alerts for this ticker."""

    return ["No alerts generated yet"];
}
EOF



#############################################
# PYTHON — byLLM Integration Layer
#############################################
echo "[INFO] Creating Python integration..."

cat << 'EOF' > "$JAC_ROOT/hco_quant_llm.py"
import os
from byllm import by

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

class HCOQuantJac:
    def __init__(self):
        self.machine = by(model_name="gemini/gemini-2.0-flash")
        self.load_folder("models")
        self.load_folder("walkers")

    def load_folder(self, subfolder):
        path = os.path.join(PROJECT_ROOT, subfolder)
        for filename in os.listdir(path):
            if filename.endswith(".jac"):
                full = os.path.join(path, filename)
                with open(full, "r") as f:
                    code = f.read()
                self.machine.load(code)

    def run(self, walker, **kwargs):
        return self.machine.run(walker, **kwargs)
EOF


#############################################
# PYTHON RUNNER
#############################################
echo "[INFO] Creating runner script..."

cat << 'EOF' > "$JAC_ROOT/jac_runner.py"
from hco_quant_llm import HCOQuantJac

jac = HCOQuantJac()

print("Running: analyze_stock...")
result = jac.run("analyze_stock", ticker="AAPL", days=30)
print(result)
EOF

chmod +x "$JAC_ROOT/jac_runner.py"

echo "[SUCCESS] Jac + byLLM structure created successfully!"
echo "Run using:"
echo "    python3 jac/jac_runner.py"
EOF
