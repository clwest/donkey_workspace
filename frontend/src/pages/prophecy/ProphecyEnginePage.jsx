import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ProphecyEnginePage() {
  const [engines, setEngines] = useState([]);
  useEffect(() => {
    apiFetch("/prophecy/engine/").then((res) => setEngines(res.results || res));
  }, []);
  return (
    <div className="container mt-4">
      <h2>Prophecy Engine</h2>
      <pre>{JSON.stringify(engines, null, 2)}</pre>
    </div>
  );
}
