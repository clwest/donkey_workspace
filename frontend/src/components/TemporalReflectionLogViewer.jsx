import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function TemporalReflectionLogViewer() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    apiFetch("/agents/reflection/logs/").then(setLogs).catch(() => setLogs([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Temporal Reflection Logs</h5>
      <ul>
        {logs.map((l) => (
          <li key={l.id}>{l.timeline_reflection_summary}</li>
        ))}
      </ul>
    </div>
  );
}
