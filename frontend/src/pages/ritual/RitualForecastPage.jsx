import React, { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualForecastPage() {
  const [forecasts, setForecasts] = useState([]);
  useEffect(() => {
    apiFetch("/ritual/forecast/").then((res) => setForecasts(res.results || res));
  }, []);
  return (
    <div className="container mt-4">
      <h2>Ritual Forecast</h2>
      <pre>{JSON.stringify(forecasts, null, 2)}</pre>
    </div>
  );
}
