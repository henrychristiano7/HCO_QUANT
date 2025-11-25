import React from "react";
import ReactDOM from "react-dom/client";
import SingleSymbol from "./components/SingleSymbol";
import MultiSymbol from "./components/MultiSymbol";

function App() {
  return (
    <div style={{ fontFamily: "Arial", padding: "20px" }}>
      <h1>📊 HCO Quant Dashboard</h1>
      <SingleSymbol />
      <hr />
      <MultiSymbol />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
