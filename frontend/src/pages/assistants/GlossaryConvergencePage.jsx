import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import apiFetch from "../../utils/apiClient";

export default function GlossaryConvergencePage() {
  const { slug } = useParams();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/assistants/${slug}/glossary/convergence/`);
      setRows(data.anchor_stats || []);
    } catch (err) {
      console.error("Failed to load convergence", err);
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
      <h2 className="mb-3">Glossary Convergence</h2>
      <div className="d-flex justify-content-end gap-2 mb-2">
        <Link
          to={`/anchor/symbolic?assistant=${slug}`}
          className="btn btn-sm btn-outline-secondary"
        >
          🧠 Symbolic Glossary Editor
        </Link>
        <Link
          to={`/anchor/mutations?assistant=${slug}`}
          className="btn btn-sm btn-outline-primary"
        >
          🧪 Review Mutation Suggestions
        </Link>
      </div>
      <button className="btn btn-outline-primary mb-3" onClick={load} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh"}
      </button>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Anchor Term</th>
            <th>Status</th>
            <th>Drift Risk</th>
            <th>Source</th>
            <th>Last Match Score</th>
            <th>Change</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.label}>
              <td>{r.label}</td>
              <td>{r.status}</td>
              <td>{r.risk || "-"}</td>
              <td>{r.mutation_source || r.source || "-"}</td>
              <td>{r.avg_score?.toFixed(2)}</td>
              <td>{r.change}</td>
            </tr>
          ))}
          {rows.length === 0 && !loading && (
            <tr>
              <td colSpan="6" className="text-muted">
                No anchors found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
