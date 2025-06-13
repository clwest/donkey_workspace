import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function DocumentReflectionsPanel({ docId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [grouped, setGrouped] = useState(false);

  useEffect(() => {
    async function fetchLogs() {
      try {
        const url = grouped
          ? `/intel/documents/${docId}/reflections/?group=true`
          : `/intel/documents/${docId}/reflections/`;
        const data = await apiFetch(url);
        setLogs(grouped ? data.groups || [] : data.reflections || []);
      } catch (err) {
        console.error("Failed to load reflections", err);
      } finally {
        setLoading(false);
      }
    }
    fetchLogs();
  }, [docId, grouped]);

  const triggerRefresh = async (slug) => {
    try {
      await apiFetch(`/assistants/${slug}/review-ingest/${docId}/`, {
        method: "POST",
      });
      const data = await apiFetch(
        grouped
          ? `/intel/documents/${docId}/reflections/?group=true`
          : `/intel/documents/${docId}/reflections/`
      );
      setLogs(grouped ? data.groups || [] : data.reflections || []);
    } catch (err) {
      console.error("Refresh failed", err);
    }
  };

  const handleSummary = async () => {
    try {
      await apiFetch(`/intel/documents/${docId}/reflect-summary/`, { method: "POST" });
      const data = await apiFetch(`/intel/documents/${docId}/reflections/?group=true`);
      setGrouped(true);
      setLogs(data.groups || []);
    } catch (err) {
      console.error("Summary failed", err);
    }
  };

  if (loading) return <div>Loading reflections...</div>;
  if (logs.length === 0) return <div>No reflections found.</div>;

  return (
    <div className="mt-4">
      <h5>📜 Reflections</h5>
      <div className="form-check form-switch mb-2">
        <input
          className="form-check-input"
          type="checkbox"
          id="groupToggle"
          checked={grouped}
          onChange={() => setGrouped(!grouped)}
        />
        <label className="form-check-label" htmlFor="groupToggle">
          Grouped View
        </label>
        <button className="btn btn-sm btn-outline-primary ms-2" onClick={handleSummary}>
          Reflect Summary
        </button>
      </div>
      <ul className="list-group mb-3">
        {grouped
          ? logs.map((g) => (
              <li key={g.slug} className="list-group-item">
                <div className="fw-bold">{g.slug}</div>
                {g.summary && <div className="small text-muted mb-1">{g.summary}</div>}
                <ul className="list-unstyled ms-3">
                  {g.items.map((r) => (
                    <li key={r.id} className="mb-1">
                      {r.is_summary && <span className="badge bg-info me-1">summary</span>}
                      {r.assistant && <span className="badge bg-secondary me-1">{r.assistant}</span>}
                      {r.summary}
                    </li>
                  ))}
                </ul>
              </li>
            ))
          : logs.map((r) => (
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
