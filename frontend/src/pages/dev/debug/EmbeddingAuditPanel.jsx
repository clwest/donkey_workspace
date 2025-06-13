import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function EmbeddingAuditPanel() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [pending, setPending] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch("/dev/embedding-audit/");
        setData(res);
        setPending(res.pending || []);
      } catch (err) {
        setError(err);
      }
    }
    load();
  }, []);

  const doFix = async (id) => {
    try {
      const res = await apiFetch(`/dev/embedding-audit/${id}/fix/`, {
        method: "PATCH",
      });
      setPending((p) => p.filter((t) => t.id !== id));
    } catch (err) {
      console.error("fix", err);
    }
  };

  const doIgnore = async (id) => {
    try {
      await apiFetch(`/dev/embedding-audit/${id}/fix/`, {
        method: "PATCH",
        body: { action: "ignore" },
      });
      setPending((p) => p.filter((t) => t.id !== id));
    } catch (err) {
      console.error("ignore", err);
    }
  };

  if (error) {
    return <div className="container py-3">Failed to load audit data.</div>;
  }

  if (!data) {
    return <div className="container py-3">Loading...</div>;
  }

  return (
    <div className="container py-3">
      <h3>Embedding Audit</h3>
      <table className="table table-sm mt-3 w-auto">
        <thead>
          <tr>
            <th>Model</th>
            <th>Mismatched</th>
            <th>Orphans</th>
          </tr>
        </thead>
        <tbody>
          {data.results.map(([model, row]) => (
            <tr key={model}>
              <td>{model}</td>
              <td>{row.mismatched}</td>
              <td>{row.orphans}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.recent_orphans && data.recent_orphans.length > 0 && (
        <details className="mt-3">
          <summary>Recent Orphans</summary>
          <pre className="mt-2 bg-light p-2">
            {data.recent_orphans
              .map((o) => `${o.embedding_id} - ${o.reason}`)
              .join("\n")}
          </pre>
        </details>
      )}
      {pending.length > 0 && (
        <div className="mt-4">
          <h5>Pending Fixes</h5>
          <div className="mb-2">
            <select value={filter} onChange={(e) => setFilter(e.target.value)} className="form-select form-select-sm w-auto d-inline">
              <option value="all">All</option>
              <option value="failed">Failed</option>
              <option value="ignored">Ignored</option>
              <option value="repaired">Repaired</option>
            </select>
          </div>
          <table className="table table-sm">
            <thead>
              <tr>
                <th>ID</th>
                <th>Content ID</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Attempts</th>
                <th>Last Attempt</th>
                <th>Notes</th>
                <th>Repaired</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {pending
                .filter((r) => filter === "all" || r.repair_status === filter)
                .map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row["embedding__content_id"]}</td>
                  <td>{row.reason}</td>
                  <td>
                    {row.repair_status}
                    {row.repair_status === "failed" && <span className="ms-1">⚠️</span>}
                  </td>
                  <td>{row.repair_attempts}</td>
                  <td>{row.last_attempt_at ? row.last_attempt_at.slice(0, 19) : ""}</td>
                  <td>{row.notes}</td>
                  <td>{row.repaired_at ? row.repaired_at.slice(0, 19) : ""}</td>
                  <td>
                    <button
                      className="btn btn-sm btn-primary me-2"
                      onClick={() => doFix(row.id)}
                    >
                      Fix
                    </button>
                    <button
                      className="btn btn-sm btn-outline-secondary"
                      onClick={() => doIgnore(row.id)}
                    >
                      Ignore
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
