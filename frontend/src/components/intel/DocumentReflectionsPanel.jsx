import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DocumentReflectionsPanel({ docId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchLogs() {
      try {
        const data = await apiFetch(`/intel/documents/${docId}/reflections/`);
        setLogs(data.reflections || []);
      } catch (err) {
        console.error("Failed to load reflections", err);
      } finally {
        setLoading(false);
      }
    }
    fetchLogs();
  }, [docId]);

  const triggerRefresh = async (slug) => {
    try {
      await apiFetch(`/assistants/${slug}/review-ingest/${docId}/`, {
        method: "POST",
      });
      const data = await apiFetch(`/intel/documents/${docId}/reflections/`);
      setLogs(data.reflections || []);
    } catch (err) {
      console.error("Refresh failed", err);
    }
  };

  if (loading) return <div>Loading reflections...</div>;
  if (logs.length === 0) return <div>No reflections found.</div>;

  return (
    <div className="mt-4">
      <h5>📜 Reflections</h5>
      <ul className="list-group mb-3">
        {logs.map((r) => (
          <li key={r.id} className="list-group-item d-flex justify-content-between align-items-start">
            <div>
              <strong>{r.assistant}</strong>
              <br />
              <small className="text-muted">{new Date(r.created_at).toLocaleString()}</small>
              <p className="mb-1">{r.summary.slice(0, 80)}</p>
            </div>
            <button className="btn btn-sm btn-outline-secondary" onClick={() => triggerRefresh(r.assistant_slug)}>
              Refresh
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
