import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function AnchorDiagnosticsPage() {
  useAuthGuard();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [orphans, setOrphans] = useState(0);

  useEffect(() => {
    apiFetch("/anchor/diagnostics/")
      .then((d) => {
        const data = d.results || [];
        setRows(data);
        setOrphans(data.filter((r) => r.chunk_count === 0).length);
      })
      .catch(() => setRows([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container my-4">Loading...</div>;

  return (
    <div className="container my-4">
      <h2 className="mb-3">
        Anchor Diagnostics
        {" "}
        <span className="badge bg-danger">{orphans} Orphaned</span>
      </h2>
      <table className="table table-sm">
        <thead>
          <tr>
            <th>Anchor</th>
            <th>Chunks</th>
            <th>Fallbacks</th>
            <th>Avg Score</th>
            <th>Assistant</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.slug}>
              <td>{r.label}</td>
              <td>{r.chunk_count}</td>
              <td>{r.fallback_count}</td>
              <td>{r.avg_score}</td>
              <td>{r.assistant || "-"}</td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td colSpan="5" className="text-muted">
                No data
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
