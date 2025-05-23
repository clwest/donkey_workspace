import { useEffect, useState } from "react";
import { fetchStabilityGraphs } from "../../api/agents";

export default function SystemStabilityPanel() {
  const [graphs, setGraphs] = useState([]);

  useEffect(() => {
    fetchStabilityGraphs()
      .then((res) => setGraphs(res.results || res))
      .catch(() => setGraphs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>System Stability Graphs</h5>
      <ul className="list-group">
        {graphs.map((g) => (
          <li key={g.id} className="list-group-item">
            Health {g.infrastructure_health}
          </li>
        ))}
        {graphs.length === 0 && (
          <li className="list-group-item text-muted">No stability data.</li>
        )}
      </ul>
    </div>
  );
}
