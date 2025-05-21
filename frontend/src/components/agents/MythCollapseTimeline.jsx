import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythCollapseTimeline() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/agents/myth-collapses/")
      .then(setLogs)
      .catch(() => setLogs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Collapse Timeline</h5>
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.collapse_reason}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No myth collapses logged.</li>
        )}
      </ul>
    </div>
  );
}
