import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryPredictionPage() {
  const [predictions, setPredictions] = useState([]);
  useEffect(() => {
    apiFetch("/memory/predict/").then((res) => setPredictions(res.results || res));
  }, []);
  return (
    <div className="container mt-4">
      <h2>Memory Prediction</h2>
      <pre>{JSON.stringify(predictions, null, 2)}</pre>
    </div>
  );
}
