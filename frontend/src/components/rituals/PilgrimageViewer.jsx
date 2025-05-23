import { useEffect, useState } from "react";
import { fetchPilgrimages } from "../../api/agents";

export default function PilgrimageViewer() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetchPilgrimages()
      .then((d) => setLogs(d.results || d))
      .catch((e) => console.error("Failed to load pilgrimages", e));
  }, []);

  return (
    <div className="my-3">
      <h5>Pilgrimages</h5>
      <ul className="list-group">
        {logs.map((log) => (
          <li key={log.id} className="list-group-item">
            {log.pilgrimage_title} {log.completed ? "✅" : ""}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No pilgrimages logged.</li>
        )}
      </ul>
    </div>
  );
}
