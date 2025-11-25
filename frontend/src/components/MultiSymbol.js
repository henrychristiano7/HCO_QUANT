import React, { useEffect, useState } from "react";
import "../App.css"; // Ensure your App.css has glow/pulse styles if needed

const MultiSymbol = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch(
        "http://127.0.0.1:8000/run_multi?symbols=AAPL,TSLA,MSFT"
      );
      const json = await res.json();
      if (json.symbols) setData(json.symbols);
    } catch (err) {
      console.error("Error fetching multi-symbol data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 bg-white rounded-2xl shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        📈 Multi-Symbol Dashboard
      </h2>
      <p className="text-gray-500 mb-6 text-sm">
        🤖 AI signals, confidence, commentary, and last updated timestamps
      </p>

      {loading ? (
        <p className="text-gray-500 animate-pulse">Loading AI signals...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse rounded-xl shadow-lg overflow-hidden">
            <thead className="bg-gradient-to-r from-blue-500 to-blue-700 text-white">
              <tr>
                <th className="p-3">Symbol</th>
                <th className="p-3">Close ($)</th>
                <th className="p-3">SMA 20</th>
                <th className="p-3">RSI</th>
                <th className="p-3">Signal</th>
                <th className="p-3">AI Confidence</th>
                <th className="p-3">AI Comment</th>
                <th className="p-3">Last Updated</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.map((item, i) => (
                <tr
                  key={i}
                  className="hover:bg-blue-50 transition-colors duration-200"
                >
                  <td className="p-3 font-semibold">{item.Symbol}</td>
                  <td className="p-3">{item.Close}</td>
                  <td className="p-3">{item.SMA_20}</td>
                  <td className="p-3">{item.RSI}</td>
                  <td
                    className={`p-2 rounded font-bold text-white text-center ${
                      item.Color === "green"
                        ? "bg-green-500 shadow-[0_0_10px_rgba(0,200,83,0.6)] animate-pulse"
                        : item.Color === "red"
                        ? "bg-red-500 shadow-[0_0_10px_rgba(213,0,0,0.6)] animate-pulse"
                        : "bg-gray-400 text-gray-900"
                    }`}
                  >
                    {item.Signal}
                  </td>
                  <td className="p-2">
                    <span className="bg-gradient-to-r from-green-400 to-blue-500 px-2 py-1 rounded-full text-white shadow-md animate-pulse">
                      {item.AI_Confidence}
                    </span>
                  </td>
                  <td className="p-3 italic text-gray-600">{item.ai_comment}</td>
                  <td className="p-3 text-sm text-gray-500">{item.Last_Updated}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default MultiSymbol;

