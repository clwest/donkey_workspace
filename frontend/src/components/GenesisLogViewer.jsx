import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function GenesisLogViewer() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/archetype-genesis/").then(setLogs);
  }, []);

  return (
    <div className="mb-3">
      <h5>Archetype Genesis Logs</h5>
      <ul>
        {logs.map((l) => (
          <li key={l.id}>
            {l.assistant} → {l.resulting_archetype}
          </li>
        ))}
      </ul>
    </div>
  );
}
