import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import useAuthGuard from "@/hooks/useAuthGuard";

export default function AssistantInsightsPage() {
  useAuthGuard();
  const { slug } = useParams();
  const [logs, setLogs] = useState(null);

  const loadLogs = async () => {
    const data = await apiFetch(`/assistants/${slug}/insights/`);
    setLogs(Array.isArray(data) ? data : []);
  };

  useEffect(() => { loadLogs(); }, [slug]);

  const accept = async (id) => {
    await apiFetch(`/assistants/${slug}/insights/${id}/accept/`, { method: "POST" });
    loadLogs();
  };

  const reject = async (id) => {
    await apiFetch(`/assistants/${slug}/insights/${id}/reject/`, { method: "POST" });
    loadLogs();
  };

  if (!logs) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-4">Insights</h2>
      {logs.length === 0 ? (
        <p>No insights yet.</p>
      ) : (
        <ul className="list-group mb-3">
          {logs.map((log) => (
            <li key={log.id} className="list-group-item">
              <p className="mb-1">{log.summary}</p>
              {log.tags && log.tags.length > 0 && (
                <small className="text-muted">{log.tags.join(", ")}</small>
              )}
              {log.proposed_prompt && !log.accepted && (
                <div className="mt-2">
                  <button className="btn btn-sm btn-success me-2" onClick={() => accept(log.id)}>
                    Accept
                  </button>
                  <button className="btn btn-sm btn-danger" onClick={() => reject(log.id)}>
                    Reject
                  </button>
                </div>
              )}
              {log.accepted && <span className="badge bg-success ms-2">Applied</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
