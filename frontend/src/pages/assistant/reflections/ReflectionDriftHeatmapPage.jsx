import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import useAuthGuard from "../../../hooks/useAuthGuard";

export default function ReflectionDriftHeatmapPage() {
  useAuthGuard();
  const { slug } = useParams();
  const [rows, setRows] = useState([]);
  const [range, setRange] = useState("30");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiFetch(`/assistants/${slug}/drift_heatmap/?days=${range}`);
      setRows(data.results || []);
    } catch (err) {
      console.error("Failed to load drift heatmap", err);
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [slug, range]);

  const badge = (score) => {
    if (score > 0.75) return "🔥";
    if (score < 0.25) return "🌱";
    return "";
  };

  return (
    <div className="container my-5">
      <h2 className="mb-4">Glossary Drift Heatmap</h2>
      <div className="d-flex gap-2 mb-3">
        <select
          className="form-select form-select-sm"
          style={{ width: "auto" }}
          value={range}
          onChange={(e) => setRange(e.target.value)}
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
        </select>
        <button className="btn btn-sm btn-outline-primary" onClick={load} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Glossary Term</th>
            <th>Avg Drift Score</th>
            <th>Reflections Affected</th>
            <th>Last Seen</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.anchor_slug}>
              <td>{r.anchor_label}</td>
              <td>{r.avg_drift_score.toFixed(2)} {badge(r.avg_drift_score)}</td>
              <td>{r.frequency}</td>
              <td>{r.timestamp ? new Date(r.timestamp).toLocaleDateString() : ""}</td>
              <td>
                {r.frequency > 3 && (
                  <a
                    href={`/anchor/mutations?anchor=${r.anchor_slug}`}
                    className="btn btn-sm btn-outline-warning"
                  >
                    Propose Fix
                  </a>
                )}
              </td>
            </tr>
          ))}
          {rows.length === 0 && !loading && (
            <tr>
              <td colSpan="5" className="text-muted">
                No drift detected.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
