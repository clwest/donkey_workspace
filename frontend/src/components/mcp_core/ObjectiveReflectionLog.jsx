import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function ObjectiveReflectionLog({ threadId }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    async function load() {
      const data = await apiFetch(`/mcp/threads/${threadId}/objective/`);
      setLogs(data.reflections || []);
    }
    load();
  }, [threadId]);

  if (!logs.length) return <p className="text-muted">No reflections yet.</p>;

  return (
    <ul className="list-group">
      {logs.map((r) => (
        <li key={r.id} className="list-group-item">
          {r.thought}
          <div className="text-muted small">
            {new Date(r.created_at).toLocaleString()}
          </div>
        </li>
      ))}
    </ul>
  );
}
