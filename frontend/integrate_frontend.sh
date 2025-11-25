#!/bin/bash

# =========================
# HCO-Quant Frontend Jac Integration Script
# =========================

# Navigate to frontend folder
cd ~/HCO-Quant/frontend || { echo "Frontend folder not found!"; exit 1; }

echo "Step 1: Installing frontend dependencies..."
npm install
npm install jac-client

echo "Step 2: Creating Jac walkers folder..."
mkdir -p src/jac_walkers

# --------------------------
# SingleSymbol Jac walker
# --------------------------
cat > src/jac_walkers/single_symbol.jac << 'EOF'
walker fetch_single_symbol(symbol: str) -> obj {
    return {
        "Symbol": symbol,
        "Close": 150 + random(20),
        "SMA_20": 145 + random(10),
        "RSI": 55 + random(15),
        "Signal": "BUY",
        "Color": "green",
        "AI_Confidence": 90,
        "ai_comment": "Momentum is positive",
        "Last_Updated": str(datetime.now())
    };
}
EOF

# --------------------------
# MultiSymbol Jac walker
# --------------------------
cat > src/jac_walkers/multi_symbol.jac << 'EOF'
walker fetch_multi_symbols(symbols: list) -> list {
    results = [];
    for s in symbols {
        results.append({
            "Symbol": s,
            "Close": 150 + random(20),
            "SMA_20": 145 + random(10),
            "RSI": 55 + random(15),
            "Signal": "BUY",
            "Color": "green",
            "AI_Confidence": 90,
            "ai_comment": "Momentum is positive",
            "Last_Updated": str(datetime.now())
        });
    }
    return results;
}
EOF

echo "Step 3: Setting environment variables for Jac client..."
# Example: default Jac client host; adjust if using remote Jac server
export JAC_CLIENT_HOST="http://localhost:8001"

echo "Step 4: Starting React frontend..."
npm start
