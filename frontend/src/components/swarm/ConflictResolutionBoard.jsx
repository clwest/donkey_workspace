import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ConflictResolutionBoard() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/conflict-resolution/")
      .then((res) => setLogs(res.results || res))
      .catch(() => setLogs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Conflict Resolutions</h5>
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.conflict_topic} - {l.resolution_method}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No conflicts logged.</li>
        )}
      </ul>
    </div>
  );
}
