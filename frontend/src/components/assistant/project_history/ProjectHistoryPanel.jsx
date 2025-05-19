import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function ProjectHistoryPanel({ projectId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectId) return;
    async function fetchLogs() {
      try {
        const data = await apiFetch(`/assistants/projects/${projectId}/history/`);
        setLogs(data);
      } catch (err) {
        console.error("Failed to load history", err);
      } finally {
        setLoading(false);
      }
    }
    fetchLogs();
  }, [projectId]);

  if (loading) return <p>Loading history...</p>;
  if (!logs.length) return <p className="text-muted">No planning history.</p>;

  const grouped = logs.reduce((acc, log) => {
    acc[log.event_type] = acc[log.event_type] || [];
    acc[log.event_type].push(log);
    return acc;
  }, {});

  return (
    <div className="mt-4">
      <h5>📚 Planning History</h5>
      {Object.entries(grouped).map(([type, items]) => (
        <details key={type} className="mb-2">
          <summary className="fw-semibold text-capitalize">
            {type.replace(/_/g, " ")}
          </summary>
          <ul className="list-group mt-2">
            {items.map((item) => (
              <li key={item.id} className="list-group-item d-flex justify-content-between">
                <span>{item.summary}</span>
                <span className="text-muted small">
                  {new Date(item.timestamp).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        </details>
      ))}
    </div>
  );
}
