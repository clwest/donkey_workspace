import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function EntropyBalancerDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    apiFetch("/agents/entropy/balance/")
      .then(setStats)
      .catch(() => setStats(null));
  }, []);

  return (
    <div className="my-3">
      <h5>Entropy Balancer</h5>
      {stats ? (
        <ul className="list-group">
          <li className="list-group-item">Memory Entropy: {stats.memory_entropy}</li>
          <li className="list-group-item">Codex Cycles: {stats.codex_cycles}</li>
          <li className="list-group-item">Active Directives: {stats.active_directives}</li>
        </ul>
      ) : (
        <p className="text-muted">No data available.</p>
      )}
    </div>
  );
}
