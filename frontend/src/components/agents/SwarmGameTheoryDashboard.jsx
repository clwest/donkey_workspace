import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SwarmGameTheoryDashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiFetch("/agents/game-dynamics/")
      .then(setData)
      .catch(() => setData(null));
  }, []);

  if (!data) return <div>Loading game dynamics...</div>;

  return (
    <div className="my-3">
      <h5>Game Theory Simulation</h5>
      <p>Diplomacy score: {data.diplomacy_score}</p>
      <p>Collaboration rate: {data.collaboration_rate}</p>
      <p>Defection rate: {data.defection_rate}</p>
      <div className="alert alert-info">{data.recommendation}</div>
    </div>
  );
}
