import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythOSWorldDashboard() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    apiFetch("/metrics/world-metrics/")
      .then(setMetrics)
      .catch(() => setMetrics(null));
  }, []);

  if (!metrics) {
    return <div className="my-3">No data.</div>;
  }

  return (
    <div className="my-3">
      <h5>MythOS World Metrics</h5>
      <ul className="list-group">
        <li className="list-group-item">
          Active Assistants: {metrics.active_assistants}
        </li>
        <li className="list-group-item">
          Rituals per Hour: {metrics.rituals_per_hour}
        </li>
        <li className="list-group-item">
          Codex Mutation Volume: {metrics.codex_mutation_volume}
        </li>
        <li className="list-group-item">Swarm Entropy: {metrics.swarm_entropy}</li>
        <li className="list-group-item">
          Belief Convergence: {metrics.belief_convergence}
        </li>
      </ul>
    </div>
  );
}
