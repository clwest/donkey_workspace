import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MythEditConsole() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/myth-edit-log/")
      .then((data) => setLogs(data.results || data))
      .catch(() => setLogs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Edit Log</h5>
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.edit_summary}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No edits logged.</li>
        )}
      </ul>
    </div>
  );
}
