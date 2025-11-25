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
