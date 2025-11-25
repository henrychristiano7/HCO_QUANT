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
