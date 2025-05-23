import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function FluxMonitorPanel() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    apiFetch("/flux-index/")
      .then((res) => setEntries(res.results || res))
      .catch(() => setEntries([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Reflective Flux Index</h5>
      <ul className="list-group">
        {entries.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.swarm_scope} – {e.insight_summary}
          </li>
        ))}
        {entries.length === 0 && (
          <li className="list-group-item text-muted">No flux data.</li>
        )}
      </ul>
    </div>
  );
}
