import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AssistantPresenceMap() {
  const [stats, setStats] = useState([]);

  useEffect(() => {
    apiFetch("/metrics/assistant-presence/")
      .then((res) => setStats(res))
      .catch(() => setStats([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Assistant Presence</h5>
      <ul className="list-group">
        {stats.map((s) => (
          <li key={s.archetype} className="list-group-item">
            {s.archetype || "Unknown"}: {s.count}
          </li>
        ))}
        {stats.length === 0 && (
          <li className="list-group-item text-muted">No presence data.</li>
        )}
      </ul>
    </div>
  );
}
