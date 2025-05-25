import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SwarmAgentMap() {
  const [routes, setRoutes] = useState([]);

  useEffect(() => {
    apiFetch("/swarm/rewire/")
      .then((res) => setRoutes(res.results || res))
      .catch(() => setRoutes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Swarm Agent Map</h5>
      <ul className="list-group">
        {routes.map((r) => (
          <li key={r.id} className="list-group-item">
            {r.from_assistant_name} → {r.to_assistant_name} ({r.route_type})
          </li>
        ))}
        {routes.length === 0 && (
          <li className="list-group-item text-muted">No routes.</li>
        )}
      </ul>
    </div>
  );
}
