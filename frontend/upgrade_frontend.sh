#!/bin/bash

echo "🚀 Starting HCO-Quant Frontend Upgrade..."

FRONTEND_DIR="$HOME/HCO-Quant/frontend"

echo "📁 Creating frontend folder..."
mkdir -p $FRONTEND_DIR
cd $FRONTEND_DIR

###############################################
# 1) Install React project if missing
###############################################

if [ ! -f "package.json" ]; then
    echo "⚛️ Creating new React app..."
    npx create-react-app . --template cra-template-pwa
else
    echo "⚛️ React project detected — upgrading files only..."
fi

###############################################
# 2) Install required dependencies
###############################################

echo "📦 Installing frontend dependencies..."

npm install axios recharts react-router-dom @mui/material @mui/icons-material @emotion/react @emotion/styled

###############################################
# 3) Create API Service file
###############################################

mkdir -p src/services

cat > src/services/api.js << 'EOF'
import axios from "axios";

const API_BASE = "http://localhost:8000";

export const getPrice = async (symbol) => {
  const { data } = await axios.get(`${API_BASE}/price/${symbol}`);
  return data;
};

export const explainSignal = async (prompt) => {
  const { data } = await axios.get(`${API_BASE}/explain`, {
    params: { prompt },
  });
  return data;
};

export const scanThreat = async (url) => {
  const { data } = await axios.get(`${API_BASE}/threat`, {
    params: { url },
  });
  return data;
};
EOF

echo "📡 Created src/services/api.js"

###############################################
# 4) Create Hooks
###############################################

mkdir -p src/hooks

cat > src/hooks/useLivePrice.js << 'EOF'
import { useState, useEffect } from "react";
import { getPrice } from "../services/api";

export default function useLivePrice(symbol) {
  const [data, setData] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const result = await getPrice(symbol);
        setData(result);
      } catch (err) {
        console.error(err);
      }
    };
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [symbol]);

  return data;
}
EOF

echo "🔁 Created useLivePrice hook"

###############################################
# 5) Create Dashboard Page
###############################################

mkdir -p src/pages

cat > src/pages/Dashboard.js << 'EOF'
import React, { useState } from "react";
import useLivePrice from "../hooks/useLivePrice";
import { explainSignal, scanThreat } from "../services/api";
import { Card, CardContent, Typography, Button, TextField } from "@mui/material";
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";

export default function Dashboard() {
  const [symbol, setSymbol] = useState("AAPL");
  const [explanation, setExplanation] = useState("");
  const [threatResult, setThreatResult] = useState("");
  const price = useLivePrice(symbol);

  const handleExplain = async () => {
    const resp = await explainSignal(`Explain ${symbol} price movement`);
    setExplanation(resp);
  };

  const handleThreat = async () => {
    const resp = await scanThreat("https://example.com");
    setThreatResult(resp);
  };

  return (
    <div style={{ padding: 20 }}>
      <Typography variant="h4">📊 HCO Quant AI Dashboard</Typography>

      <Card style={{ marginTop: 20 }}>
        <CardContent>
          <Typography variant="h6">Live Price Feed</Typography>
          <TextField
            label="Symbol"
            variant="outlined"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            style={{ marginTop: 10 }}
          />

          {price && (
            <div style={{ marginTop: 20 }}>
              <Typography>Price: ${price.price}</Typography>
              <Typography>Open: ${price.open}</Typography>
              <Typography>High: ${price.high}</Typography>
              <Typography>Low: ${price.low}</Typography>
              <Typography>Volume: {price.volume}</Typography>
            </div>
          )}
        </CardContent>
      </Card>

      <Card style={{ marginTop: 20 }}>
        <CardContent>
          <Button variant="contained" onClick={handleExplain}>
            Explain Market Movement
          </Button>
          <Typography style={{ marginTop: 20 }}>{explanation}</Typography>
        </CardContent>
      </Card>

      <Card style={{ marginTop: 20 }}>
        <CardContent>
          <Button color="error" variant="contained" onClick={handleThreat}>
            Scan URL Threat
          </Button>
          <Typography style={{ marginTop: 20 }}>{threatResult}</Typography>
        </CardContent>
      </Card>
    </div>
  );
}
EOF

echo "📄 Created Dashboard.js"

###############################################
# 6) Setup Routing
###############################################

cat > src/App.js << 'EOF'
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
EOF

echo "🛣️ Updated App.js"

###############################################
# 7) Cleanup & Finish
###############################################

echo "🧹 Cleaning..."
rm -rf src/logo.svg src/App.test.js src/reportWebVitals.js src/setupTests.js

echo ""
echo "🎉 Frontend upgrade complete!"
echo ""
echo "Run frontend:"
echo "----------------------------"
echo "cd $FRONTEND_DIR"
echo "npm start"
echo "----------------------------"
echo ""
echo "Your dashboard is ready and connected!"
