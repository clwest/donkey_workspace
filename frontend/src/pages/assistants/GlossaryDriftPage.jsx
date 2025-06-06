import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../utils/apiClient";
import useAuthGuard from "../../hooks/useAuthGuard";

export default function GlossaryDriftPage() {
  useAuthGuard();
  const { slug } = useParams();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await apiFetch(`/assistants/${slug}/rag_drift_report/`);
      setRows(res || []);
    } catch (err) {
      console.error("Failed to load drift report", err);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [slug]);

  const rowClass = (risk) => {
    if (risk === "high") return "table-danger";
    if (risk === "medium") return "table-warning";
    return "table-success";
  };

  return (
    <div className="container my-5">
      <h2 className="mb-3">Glossary Drift Report</h2>
      <button className="btn btn-outline-primary mb-3" onClick={load} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh"}
      </button>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Term</th>
            <th>Avg Score</th>
            <th>Fallback Logs</th>
            <th>Last Chunk</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.term} className={rowClass(r.risk)}>
              <td>{r.term}</td>
              <td>{r.avg_score.toFixed ? r.avg_score.toFixed(2) : r.avg_score}</td>
              <td>{r.fallback_count}</td>
              <td className="small text-muted">{r.last_chunk_id || "—"}</td>
              <td>{r.risk}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
