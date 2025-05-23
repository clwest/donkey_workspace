import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function MemoryReplayPanel() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/memory/replay/")
      .then((res) => setLogs(res.results || res))
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div>Loading memory replay...</div>;
  }

  return (
    <div className="my-3">
      <h5>Memory Replay</h5>
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.title || l.id}
          </li>
        ))}
        {logs.length === 0 && (
          <li className="list-group-item text-muted">No replay logs.</li>
        )}
      </ul>
    </div>
  );
}
