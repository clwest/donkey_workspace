import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythEngineMonitor() {
  const [engines, setEngines] = useState([]);

  useEffect(() => {
    apiFetch("/myth-engines/")
      .then((res) => setEngines(res.results || res))
      .catch(() => setEngines([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Engine Instances</h5>
      <ul className="list-group">
        {engines.map((e) => (
          <li key={e.id} className="list-group-item">
            {e.instance_name} – {e.engine_status}
          </li>
        ))}
        {engines.length === 0 && (
          <li className="list-group-item text-muted">No engines running.</li>
        )}
      </ul>
    </div>
  );
}
