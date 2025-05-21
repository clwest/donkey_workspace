import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function StrategyScoreboard() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    apiFetch("/agents/strategy-score/")
      .then(setMetrics)
      .catch((err) => console.error("Failed to load strategy score", err));
  }, []);

  if (!metrics) return <div className="my-4">Loading...</div>;

  return (
    <div className="my-4">
      <h4 className="mb-3">Strategy Scoreboard</h4>
      <ul className="list-unstyled">
        <li>Alignment: {metrics.alignment}</li>
        <li>Participation: {metrics.participation}</li>
        <li>Reflection Depth: {metrics.reflection_depth}</li>
        <li>Cohesion: {metrics.cohesion}</li>
      </ul>
    </div>
  );
}
