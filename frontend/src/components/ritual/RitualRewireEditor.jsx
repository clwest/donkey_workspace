import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function RitualRewireEditor() {
  const [routes, setRoutes] = useState([]);

  useEffect(() => {
    apiFetch("/swarm/proposals/")
      .then((res) => setRoutes(res.results || res))
      .catch(() => setRoutes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Ritual Routes</h5>
      <ul className="list-group mb-2">
        {routes.map((r) => (
          <li key={r.id} className="list-group-item">
            {r.initiator_name} → {r.receiver_name} ({r.context_clause})
          </li>
        ))}
        {routes.length === 0 && (
          <li className="list-group-item text-muted">No routes.</li>
        )}
      </ul>
      <p className="text-muted small">Drift and feedback integration pending.</p>
    </div>
  );
}
