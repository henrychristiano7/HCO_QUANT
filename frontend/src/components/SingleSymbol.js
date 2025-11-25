import React, { useEffect, useState } from "react";
import "../App.css"; // import global styles for glow/pulse effects

const SingleSymbol = () => {
  const [symbol, setSymbol] = useState("AAPL");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSingle = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://127.0.0.1:8000/run?symbol=${symbol}`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Error fetching single symbol:", err);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSingle();
    const interval = setInterval(fetchSingle, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, [symbol]);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        📊 Single Symbol Dashboard
      </h2>
      <p className="text-gray-500 mb-4 text-sm">
        🤖 AI signals, confidence, and rationale for {symbol}
      </p>

      {/* Symbol input */}
      <div className="mb-6 flex justify-center">
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          className="border border-gray-300 px-3 py-2 rounded-lg text-center focus:ring-2 focus:ring-blue-500 focus:outline-none"
          placeholder="Enter Symbol (e.g. AAPL)"
        />
      </div>

      {loading ? (
        <p className="text-gray-500 animate-pulse">Loading AI signal...</p>
      ) : data ? (
        <div className="bg-white shadow-xl rounded-2xl p-6 max-w-md mx-auto transition hover:shadow-2xl">
          <h3 className="text-xl font-semibold mb-4">{data.Symbol}</h3>
          <p className="mb-1">Close: ${data.Close}</p>
          <p className="mb-1">SMA 20: {data.SMA_20}</p>
          <p className="mb-1">RSI: {data.RSI}</p>
          <p
            className={`mt-2 px-3 py-1 rounded font-bold text-center text-white ${
              data.Color === "green"
                ? "bg-green-500 shadow-[0_0_12px_rgba(0,200,83,0.7)] animate-pulse"
                : data.Color === "red"
                ? "bg-red-500 shadow-[0_0_12px_rgba(213,0,0,0.7)] animate-pulse"
                : "bg-gray-400 text-gray-900"
            }`}
          >
            Signal: {data.Signal}
          </p>
          <p className="mt-2 font-semibold">
            AI Confidence:{" "}
            <span className="bg-gradient-to-r from-green-400 to-blue-500 px-2 py-1 rounded-full text-white shadow-md animate-pulse">
              {data.confidence}%
            </span>
          </p>
          <p className="italic mt-2 text-gray-600">Rationale: {data.ai_comment}</p>
          <p className="text-sm text-gray-500 mt-3">Last Updated: {data.Last_Updated}</p>
        </div>
      ) : (
        <p className="text-red-500">No data available for {symbol}</p>
      )}
    </div>
  );
};

export default SingleSymbol;

