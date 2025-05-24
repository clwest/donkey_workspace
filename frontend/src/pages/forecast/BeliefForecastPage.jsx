import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BeliefForecastPage() {
  const [data, setData] = useState(null);
  useEffect(() => {
    apiFetch("/forecast/belief/").then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="container my-5">
      <h1 className="mb-3">Belief Resonance Forecast</h1>
      {data ? <pre>{JSON.stringify(data, null, 2)}</pre> : <div>Loading forecast...</div>}
    </div>
  );
}
