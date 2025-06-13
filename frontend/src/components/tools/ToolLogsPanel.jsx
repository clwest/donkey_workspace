import { useEffect, useState } from "react";
import { fetchToolLogs } from "../../api/tools";

export default function ToolLogsPanel({ toolId }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (!toolId) return;
    fetchToolLogs(toolId).then(setLogs).catch(() => setLogs([]));
  }, [toolId]);

  return (
    <div className="mt-3">
      <h5>Recent Logs</h5>
      <ul className="list-group">
        {logs.map((l) => (
          <li key={l.id} className="list-group-item">
            {l.success ? "✅" : "❌"} {l.created_at}
          </li>
        ))}
      </ul>
    </div>
  );
}
