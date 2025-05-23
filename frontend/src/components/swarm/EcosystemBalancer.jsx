import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function EcosystemBalancer() {
  const [engines, setEngines] = useState([]);

  useEffect(() => {
    apiFetch("/reflective-ecosystem/")
      .then((res) => setEngines(res.results || res))
      .catch(() => setEngines([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Reflective Ecosystem Engines</h5>
      <ul className="list-group">
        {engines.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.scope}
          </li>
        ))}
        {engines.length === 0 && (
          <li className="list-group-item text-muted">No ecosystem engines.</li>
        )}
      </ul>
    </div>
  );
}
