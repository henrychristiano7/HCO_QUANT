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
