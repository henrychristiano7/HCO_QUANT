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
