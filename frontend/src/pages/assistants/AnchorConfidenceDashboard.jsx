import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function AnchorConfidenceDashboard() {
  useAuthGuard();
  const { slug } = useParams();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/assistants/${slug}/anchors/confidence/`);
      setRows(data.results || []);
    } catch (err) {
      console.error("Failed to load anchor confidence", err);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [slug]);

  return (
    <div className="container my-5">
      <h2 className="mb-3">Anchor Confidence Dashboard</h2>
      <button className="btn btn-outline-secondary mb-2" onClick={load} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh"}
      </button>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Anchor</th>
            <th>Avg Score</th>
            <th>Fallback Rate</th>
            <th>Glossary Hits %</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.slug}>
              <td>{r.label}</td>
              <td>{r.avg_score.toFixed(2)}</td>
              <td>{(r.fallback_rate * 100).toFixed(0)}%</td>
              <td>{(r.glossary_hit_pct * 100).toFixed(0)}%</td>
            </tr>
          ))}
          {rows.length === 0 && !loading && (
            <tr>
              <td colSpan="4" className="text-muted">
                No data.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
